from __future__ import print_function
from bcc import BPF
from time import sleep, strftime
import argparse


bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>
#include <linux/list.h>

typedef struct disk_key {
    char disk[DISK_NAME_LEN];
    u64 slot;
} disk_key_t;

typedef struct disk_bio {
    u64 bi_vcnt;
} disk_bio_t;

BPF_HASH(longbio, struct disk_bio *);
BPF_HASH(start, struct request *);
BPF_HISTOGRAM(dist);

static void bio_dump(struct bio *bio)
{
   struct bio_vec *bi_vecs;
   int i;
   struct address_space *mapping;
   struct inode *inode;
   struct page *page;
   struct dentry *dentry;
   struct hlist_head   *i_dentry;
   struct hlist_node *first;

   bi_vecs = bio->bi_io_vec;
   page = bi_vecs->bv_page;
   mapping = page->mapping;
   inode = mapping->host;

   //dentry = hlist_entry(inode->i_dentry.first, struct dentry, d_u.d_alias);
   i_dentry = &inode->i_dentry;
   first = i_dentry->first;
   dentry = container_of(first, struct dentry, d_u.d_alias);

   bpf_trace_printk("bio->bi_vcnt:%lx", bio->bi_vcnt);
   for (i = 0; i <= 2; ++i) {
        bpf_trace_printk("bv_page:%lx bv_len:%lx bv_offset:%lx", (unsigned long)bi_vecs->bv_page, (unsigned long)bi_vecs->bv_len, (unsigned long)bi_vecs->bv_offset);
        bi_vecs++;
        if ( (i + 1) == bio->bi_vcnt)
            break;
   }
}

// time block I/O
int trace_req_start(struct pt_regs *ctx, struct request *req)
{
    u64 ts = bpf_ktime_get_ns();
    //disk_bio_t d_bio;
    //struct bio *bio =  req->bio;
    //d_bio.bi_vcnt = req->bio->bi_vcnt;

    bio_dump(req->bio);
    //longbio.update(&d_bio, &ts);
    start.update(&req, &ts);
    return 0;
}

// output
int trace_req_done(struct pt_regs *ctx, struct request *req)
{
    u64 *tsp, delta;
    struct bio *bio =  req->bio;

    // fetch timestamp and calculate delta
    tsp = start.lookup(&req);
    if (tsp == 0) {
        return 0;   // missed issue
    }
    delta = bpf_ktime_get_ns() - *tsp;

    delta /= 1000;
    dist.increment(bpf_log2l(delta));

    start.delete(&req);
    return 0;
}
"""

bpf_text = bpf_text.replace('STORAGE', 'BPF_HISTOGRAM(dist);')
bpf_text = bpf_text.replace('STORE',
    'dist.increment(bpf_log2l(delta));')
# load BPF program
b = BPF(text=bpf_text)
#b.attach_kprobe(event="blk_start_request", fn_name="trace_req_start")
b.attach_kprobe(event="blk_mq_start_request", fn_name="trace_req_start")
b.attach_kprobe(event="blk_account_io_done",
    fn_name="trace_req_done")

label = "msecs"
exiting = 0

dist = b.get_table("dist")
while (1):
    try:
        sleep(1)
    except KeyboardInterrupt:
        exiting = 1

    dist.print_log2_hist(label, "disk")
    #dist.clear()

    if exiting:
        exit()
