#!/usr/bin/python
from __future__ import print_function
from bcc import BPF
from time import sleep, strftime
import argparse


bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>
#include <linux/compaction.h>
#include <linux/migrate_mode.h>

struct compact_control {
    struct list_head freepages; /* List of free pages to migrate to */
    struct list_head migratepages;  /* List of pages being migrated */
    struct zone *zone;
    unsigned long nr_freepages; /* Number of isolated free pages */
    unsigned long nr_migratepages;  /* Number of pages to migrate */
    unsigned long total_migrate_scanned;
    unsigned long total_free_scanned;
    unsigned long free_pfn;     /* isolate_freepages search base */
    unsigned long migrate_pfn;  /* isolate_migratepages search base */
    unsigned long last_migrated_pfn;/* Not yet flushed page being freed */
    const gfp_t gfp_mask;       /* gfp mask of a direct compactor */
    int order;          /* order a direct compactor needs */
    int migratetype;        /* migratetype of direct compactor */
    const unsigned int alloc_flags; /* alloc flags of a direct compactor */
    const int classzone_idx;    /* zone index of a direct compactor */
    enum migrate_mode mode;     /* Async or sync migration mode */
    bool ignore_skip_hint;      /* Scan blocks even if marked skip */
    bool no_set_skip_hint;      /* Don't mark blocks for skipping */
    bool ignore_block_suitable; /* Scan blocks considered unsuitable */
    bool direct_compaction;     /* False from kcompactd or /proc/... */
    bool whole_zone;        /* Whole zone should/has been scanned */
    bool contended;         /* Signal lock or sched contention */
    bool finishing_block;       /* Finishing current pageblock */
};
typedef struct page *new_page_t(struct page *page, unsigned long private);
typedef void free_page_t(struct page *page, unsigned long private);

int kprobe__compact_zone(struct pt_regs *ctx, struct zone *zone, struct compact_control *cc)
{

    bpf_trace_printk("migrtetype1:%d \\n", cc->migratetype);
    return 0;
}

/*
int kprobe__isolate_migratepages_block(struct pt_regs *ctx, struct compact_control *cc, unsigned long low_pfn,
            unsigned long end_pfn, isolate_mode_t isolate_mode)
{
    bpf_trace_printk("block %lx~%lx %d \\n", low_pfn, end_pfn, cc->nr_migratepages);
    return 0;
}
*/

static struct page *kprobe__compaction_alloc(struct pt_regs *ctx, struct page *migratepage, unsigned long data)
{
    struct compact_control *cc = data;
    bpf_trace_printk("alloc %d \\n", cc->nr_migratepages);
    return 0;
}

static struct page *kprobe__compaction_free(struct pt_regs *ctx, struct page *migratepage, unsigned long data)
{
    struct compact_control *cc = data;
    bpf_trace_printk("free %d \\n", cc->nr_migratepages);
    return 0;

}
"""


# load BPF program
b = BPF(text=bpf_text)


exiting = 0
while (1):
    try:
        sleep(1)
    except KeyboardInterrupt:
        exiting = 1
    if exiting == 1:
		exit()



