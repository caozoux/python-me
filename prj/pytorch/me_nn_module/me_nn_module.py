"""me_nn_module —— 简要实现 PyTorch 的 nn.Module(教学用)

只借用 torch 的底层算子(Tensor / autograd / functional),而 nn.Module 的
"注册 + 递归遍历 + __call__ 分发"机制全部自研,脉络与真实实现
(torch/nn/modules/module.py)一致:

  1. __setattr__ 拦截 —— Parameter 落入 _parameters,子 Module 落入 _modules,
     register_buffer 注册的张量落入 _buffers,其余照常进 __dict__。
  2. __getattr__ 兜底 —— 常规属性查不到时再回头查这三张表,于是
     `self.weight`、`self.layer1` 看起来像普通属性,实际存在注册表里。
  3. __call__ => forward —— 并触发 pre/post 钩子(真实 torch 的 _call_impl)。
  4. parameters / modules / state_dict / train / to 等都是对三张表的递归遍历。

因为 Parameter 直接继承真实 torch.Tensor,本实现可无缝接入 torch.optim 与
autograd:demo 里用真实 SGD 把一个小 MLP 训练收敛。

运行:python me_nn_module.py
"""
import math
from collections import OrderedDict
from typing import Any, Callable, Iterator, Optional, Tuple

import torch
import torch.nn.functional as F


# --------------------------------------------------------------------------- #
# Parameter:可训练参数 = requires_grad=True 的 Tensor 子类
# --------------------------------------------------------------------------- #
class Parameter(torch.Tensor):
    """真实 torch 中 Parameter 的最小复刻。

    _make_subclass 是 torch 官方的 Tensor 子类化入口:生成 cls 类型的实例,
    与 data 共享存储,并将其置为带 requires_grad 的叶子节点。
    """

    def __new__(cls, data: Optional[torch.Tensor] = None,
                requires_grad: bool = True) -> "Parameter":
        if data is None:
            data = torch.empty(0)
        if not isinstance(data, torch.Tensor):
            data = torch.as_tensor(data)
        if data.requires_grad:          # _make_subclass 只接受无梯度的张量
            data = data.detach()
        return torch.Tensor._make_subclass(cls, data, requires_grad)


# --------------------------------------------------------------------------- #
# 钩子句柄:持有钩子在字典里的 id,支持 remove() 注销
# --------------------------------------------------------------------------- #
class HookHandle:
    def __init__(self, hooks: "OrderedDict[int, Callable]", hook_id: int) -> None:
        self._hooks, self._id = hooks, hook_id

    def remove(self) -> None:
        self._hooks.pop(self._id, None)


# --------------------------------------------------------------------------- #
# Module:一切网络结构的基类(简化版)
# --------------------------------------------------------------------------- #
class Module:
    def __init__(self) -> None:
        # 三张注册表是 nn.Module 一切魔法的根基,全部按名字有序
        self._parameters = OrderedDict()          # name -> Parameter
        self._buffers = OrderedDict()             # name -> Tensor(非训练态缓存)
        self._modules = OrderedDict()             # name -> Module
        self.training = True                      # train()/eval() 切换的标志
        self._forward_pre_hooks: "OrderedDict[int, Callable]" = OrderedDict()
        self._forward_hooks: "OrderedDict[int, Callable]" = OrderedDict()

    # ---------------- 注册机制:__setattr__ / __getattr__ ------------------ #
    def __setattr__(self, name: str, value: Any) -> None:
        params = self.__dict__.get('_parameters')

        if isinstance(value, Parameter):
            if params is None:
                raise AttributeError(
                    "cannot assign parameter before Module.__init__() call")
            # 若之前是 Parameter、现在被覆盖,则注销旧的(真实 torch 行为)
            remove_from = (self.__dict__, self._buffers, self._modules)
            for d in remove_from:
                d.pop(name, None)
            params[name] = value
            return

        if params is not None and name in params:
            # 原名曾是参数,如今赋了非 Parameter 值:只允许 None(置空)
            if value is not None:
                raise TypeError(
                    f"cannot assign '{type(value).__name__}' as parameter '{name}'")
            params[name] = None
            return

        modules = self.__dict__.get('_modules')
        if isinstance(value, Module):
            if modules is None:
                raise AttributeError(
                    "cannot assign module before Module.__init__() call")
            modules[name] = value
            return

        buffers = self.__dict__.get('_buffers')
        if buffers is not None and name in buffers:
            # 已注册的 buffer 只能被 Tensor(或 None)覆盖
            if value is not None and not isinstance(value, torch.Tensor):
                raise TypeError(
                    f"cannot assign '{type(value).__name__}' as buffer '{name}'")
            buffers[name] = value
            return

        # 普通属性(含普通 Tensor):照常进 __dict__,不参与注册。
        # 真实 torch 会直接报错,提示改用 register_buffer;这里从宽处理。
        object.__setattr__(self, name, value)

    def __getattr__(self, name: str) -> Any:
        # 仅当常规属性查找(__dict__ / 类属性)失败后才会被调用,
        # 依次回查三张注册表 —— 这就是 `self.weight` 能"凭空"出现的原因
        if '_parameters' in self.__dict__:
            _parameters = self.__dict__['_parameters']
            if name in _parameters:
                return _parameters[name]
        if '_buffers' in self.__dict__:
            _buffers = self.__dict__['_buffers']
            if name in _buffers:
                return _buffers[name]
        if '_modules' in self.__dict__:
            _modules = self.__dict__['_modules']
            if name in _modules:
                return _modules[name]
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'")

    # ---------------------------- 前向与钩子 ------------------------------- #
    def forward(self, *args, **kwargs):
        raise NotImplementedError(
            f"Module [{type(self).__name__}] 应实现 forward()")

    def __call__(self, *args, **kwargs):
        # 真实 torch 把 __call__ 指向 _wrapped_call_impl -> _call_impl,
        # 效果一致:先 pre 钩子,再 forward,后 post 钩子(可替换输出)
        for hook in self._forward_pre_hooks.values():
            hook(self, args)
        out = self.forward(*args, **kwargs)
        for hook in self._forward_hooks.values():
            ret = hook(self, args, out)
            if ret is not None:           # 返回非 None 则替换 forward 的输出
                out = ret
        return out

    def register_forward_pre_hook(self, hook) -> HookHandle:
        self._forward_pre_hooks[id(hook)] = hook
        return HookHandle(self._forward_pre_hooks, id(hook))

    def register_forward_hook(self, hook) -> HookHandle:
        self._forward_hooks[id(hook)] = hook
        return HookHandle(self._forward_hooks, id(hook))

    # -------------------------- 注册 API ---------------------------------- #
    def register_buffer(self, name: str, tensor: Optional[torch.Tensor]) -> None:
        """注册随模型走但不需要梯度的张量(如 BN 的 running_mean)。"""
        self._buffers[name] = tensor

    def register_parameter(self, name: str, param: Optional[Parameter]) -> None:
        self._parameters[name] = param

    def add_module(self, name: str, module: Optional["Module"]) -> None:
        if module is not None and not isinstance(module, Module):
            raise TypeError(f"{type(module).__name__} is not a Module")
        self._modules[name] = module

    # ------------------------- 递归遍历 ----------------------------------- #
    def named_modules(self, memo: Optional[set] = None, prefix: str = '',
                      remove_duplicate: bool = True
                      ) -> Iterator[Tuple[str, "Module"]]:
        if memo is None:
            memo = set()
        if self in memo:                  # 共享子模块只遍历一次
            return
        if remove_duplicate:
            memo.add(self)
        yield prefix, self
        for name, module in self._modules.items():
            if module is None:
                continue
            sub_prefix = f'{prefix}.{name}' if prefix else name
            yield from module.named_modules(memo, sub_prefix, remove_duplicate)

    def modules(self) -> Iterator["Module"]:
        for _, module in self.named_modules():
            yield module

    def named_children(self) -> Iterator[Tuple[str, "Module"]]:
        yield from self._modules.items()

    def children(self) -> Iterator["Module"]:
        yield from self._modules.values()

    def _named_members(self, get_members_fn, prefix: str = '', recurse: bool = True,
                       remove_duplicate: bool = True) -> Iterator[Tuple[str, Any]]:
        memo = set() if remove_duplicate else None
        if recurse:
            module_iter = self.named_modules(prefix=prefix)
        else:
            module_iter = iter([(prefix, self)])
        for module_prefix, module in module_iter:
            for k, v in get_members_fn(module):
                if v is None or (memo is not None and v in memo):
                    continue
                if memo is not None:
                    memo.add(v)
                yield module_prefix + ('.' if module_prefix else '') + k, v

    def named_parameters(self, prefix: str = '', recurse: bool = True,
                         remove_duplicate: bool = True
                         ) -> Iterator[Tuple[str, Parameter]]:
        yield from self._named_members(
            lambda m: m._parameters.items(),
            prefix, recurse, remove_duplicate)

    def parameters(self, recurse: bool = True) -> Iterator[Parameter]:
        for _, param in self.named_parameters(recurse=recurse):
            yield param

    def apply(self, fn: Callable[["Module"], None]) -> "Module":
        """后序遍历地对每个模块执行 fn(常用于自定义初始化)。"""
        for module in self.children():
            module.apply(fn)
        fn(self)
        return self

    # --------------------------- 训练态 ----------------------------------- #
    def train(self, mode: bool = True) -> "Module":
        self.training = mode
        for module in self.children():
            module.train(mode)
        return self

    def eval(self) -> "Module":
        return self.train(False)

    def zero_grad(self) -> None:
        for p in self.parameters():
            p.grad = None              # 现代 torch 默认 set-to-None

    def requires_grad_(self, requires_grad: bool = True) -> "Module":
        for p in self.parameters():
            p.requires_grad_(requires_grad)
        return self

    # --------------------------- 设备迁移 ---------------------------------- #
    def _apply(self, fn: Callable[[torch.Tensor], torch.Tensor]) -> "Module":
        for p in self._parameters.values():
            if p is not None:
                p.data = fn(p.data)    # 用 .data 原地替换,保持注册表身份不变
                if p.grad is not None:
                    p.grad = fn(p.grad)
        for name, buf in self._buffers.items():
            if buf is not None:
                self._buffers[name] = fn(buf)
        for module in self.children():
            module._apply(fn)
        return self

    def to(self, device) -> "Module":
        return self._apply(lambda t: t.to(device))

    def cuda(self) -> "Module":
        return self.to('cuda')

    def cpu(self) -> "Module":
        return self.to('cpu')

    # ------------------------ state_dict 存取 ------------------------------ #
    def state_dict(self, prefix: str = '') -> "OrderedDict[str, torch.Tensor]":
        out: "OrderedDict[str, torch.Tensor]" = OrderedDict()
        for name, p in self._parameters.items():
            if p is not None:
                out[prefix + name] = p.detach()   # 注意:与真实 torch 一样共享存储
        for name, b in self._buffers.items():
            if b is not None:
                out[prefix + name] = b.detach()
        for name, module in self._modules.items():
            if module is not None:
                out.update(module.state_dict(prefix + name + '.'))
        return out

    def load_state_dict(self, state_dict, strict: bool = True) -> None:
        own = self.state_dict()
        missing = [k for k in own if k not in state_dict]
        unexpected = [k for k in state_dict if k not in own]
        for key, tensor in state_dict.items():
            if key not in own:
                continue
            if own[key].shape != tensor.shape:
                raise RuntimeError(
                    f"size mismatch for {key}: copying from "
                    f"{tuple(tensor.shape)} into {tuple(own[key].shape)}")
            own[key].copy_(tensor)     # detach 视图共享存储,copy_ 直接写回模型
        if strict and (missing or unexpected):
            raise RuntimeError(
                f"missing keys: {missing}, unexpected keys: {unexpected}")

    # ----------------------------- 表示 ----------------------------------- #
    def extra_repr(self) -> str:
        return ''

    def __repr__(self) -> str:
        lines = []
        if (extra := self.extra_repr()):
            lines.append(extra)
        for key, module in self._modules.items():
            lines.append(f'({key}): ' + _addindent(repr(module), 2))
        main = f'{self.__class__.__name__}('
        if lines:
            main += '\n  ' + '\n  '.join(lines) + '\n'
        return main + ')'


def _addindent(s: str, num_spaces: int) -> str:
    """把多行字符串整体缩进 num_spaces 空格(首行除外),同真实 torch。"""
    first, *rest = s.split('\n')
    return '\n'.join([first] + [' ' * num_spaces + line for line in rest])


# --------------------------------------------------------------------------- #
# 用本框架搭几个基本层,验证机制自洽
# --------------------------------------------------------------------------- #
class Linear(Module):
    def __init__(self, in_features: int, out_features: int, bias: bool = True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.weight = Parameter(torch.empty(out_features, in_features))
        if bias:
            self.bias = Parameter(torch.empty(out_features))
        else:
            self.bias = None           # None 会走普通 __dict__,不进注册表
        self.reset_parameters()

    def reset_parameters(self) -> None:
        bound = 1.0 / math.sqrt(self.in_features)   # 简化版均匀初始化
        self.weight.data.uniform_(-bound, bound)
        if self.bias is not None:
            self.bias.data.uniform_(-bound, bound)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return F.linear(x, self.weight, self.bias)

    def extra_repr(self) -> str:
        return (f'in_features={self.in_features}, '
                f'out_features={self.out_features}, bias={self.bias is not None}')


class ReLU(Module):
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return F.relu(x)


class Dropout(Module):
    """训练态按概率置零并放大 1/(1-p);eval 态直通 —— 展示 training 标志的用途。"""

    def __init__(self, p: float = 0.5):
        super().__init__()
        self.p = p

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return F.dropout(x, self.p, self.training)

    def extra_repr(self) -> str:
        return f'p={self.p}'


class Sequential(Module):
    def __init__(self, *modules: Module):
        super().__init__()
        for idx, module in enumerate(modules):
            self.add_module(str(idx), module)

    def forward(self, x):
        for module in self._modules.values():
            x = module(x)
        return x


# --------------------------------------------------------------------------- #
# Demo:组网、训练收敛、钩子、train/eval、state_dict、设备迁移
# --------------------------------------------------------------------------- #
def _make_mlp() -> Sequential:
    return Sequential(
        Linear(2, 16), ReLU(),
        Linear(16, 16), ReLU(),
        Linear(16, 1),
    )


def main() -> None:
    torch.manual_seed(0)
    print('=' * 62)

    # 1) 组网与打印:用法与真实 nn.Module 完全一致
    model = _make_mlp()
    print('[1] 模型结构 (__repr__):')
    print(model)
    print('参数量:', sum(p.numel() for p in model.parameters()))
    names = [name for name, _ in model.named_parameters()]
    print('named_parameters 前 3 项:', names[:3])

    # 2) 训练:parameters() 直接交给真实 torch.optim,验证注册机制自洽
    print('\n[2] 训练一个拟合 y = x0^2 + x1 的小 MLP:')
    x = torch.rand(256, 2) * 4 - 2
    y = x[:, :1] ** 2 + x[:, 1:]
    opt = torch.optim.SGD(model.parameters(), lr=0.05, momentum=0.9)
    model.train()
    for step in range(1, 401):
        opt.zero_grad()
        loss = F.mse_loss(model(x), y)
        loss.backward()
        opt.step()
        if step % 100 == 0:
            print(f'    step {step:3d}   loss = {loss.item():.4f}')

    # 3) 前向钩子:__call__ 分发机制
    print('\n[3] 前向钩子:')
    def shape_hook(module, inputs, output):
        print(f'    [hook] {type(module).__name__}: '
              f'in {tuple(inputs[0].shape)} -> out {tuple(output.shape)}')
    first_linear = next(m for m in model.modules() if isinstance(m, Linear))
    handle = first_linear.register_forward_hook(shape_hook)
    _ = model(x[:2])
    handle.remove()
    print('    (钩子已注销,再跑一次无输出)')
    _ = model(x[:2])

    # 4) train/eval 与 Dropout
    print('\n[4] training 标志 + Dropout:')
    drop = Dropout(0.9)
    z = torch.ones(1000)
    drop.train()
    print(f'    train: 置零比例 = {(drop(z) == 0).float().mean().item():.2f}')
    drop.eval()
    print(f'    eval : 全直通   = {bool(torch.all(drop(z) == 1))}')

    # 5) state_dict 保存 / 恢复
    print('\n[5] state_dict 保存与恢复:')
    state = model.state_dict()
    print('    keys:', list(state.keys()))
    clone = _make_mlp()
    clone.load_state_dict(state)
    xt = x[:8]
    print('    恢复后前向一致:', bool(torch.allclose(model(xt), clone(xt))))

    # 6) 设备迁移
    print('\n[6] 设备迁移:')
    if torch.cuda.is_available():
        model.to('cuda')
        print('    .to(cuda) 后权重设备:',
              next(model.parameters()).device)
        model.cpu()
    else:
        model.cpu()
        print('    无 GPU,停留在:', next(model.parameters()).device)
    print('=' * 62)


if __name__ == '__main__':
    main()
