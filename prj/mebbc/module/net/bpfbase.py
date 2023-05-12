
class KprobeBase(object):

    """Docstring for KprobeBase. """

    def __init__(self, funcname):
        """TODO: to be defined. """
        self.funcname=funcname

    def __init__(self ):
        """TODO: to be defined. """
        self.funcname=""

    def filter(self, cpu, pid):
        if pid:
            self.bpf_text = self.bpf_text.replace(b'FILTERPID',
                b"""u32 pid = bpf_get_current_pid_tgid() >> 32;
                   if (pid != %d) { return 0; }""" % args.pid)
        else:
            self.bpf_text = self.bpf_text.replace(b'FILTERPID', b'')

        if cpu:
            self.bpf_text = self.bpf_text.replace(b'FILTERCPU',
                b"""u32 cpu = bpf_get_smp_processor_id();
                   if (cpu != %d) { return 0; }""" % int(args.cpu))
        else:
            self.bpf_text = self.bpf_text.replace(b'FILTERCPU', b'')

    # attach kprobe event
    def attach(self,bpf):
        pass

    # load bpf txt to bpf
    def append(self):
        return self.bpf_text

    def update(self):
        pass

    def dump(self):
        print(self.bpf_text)

    def report(self, bpf):
        pass

