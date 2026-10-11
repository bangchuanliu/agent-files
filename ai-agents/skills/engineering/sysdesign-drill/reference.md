# System Design Drill Reference

Verifier-only tables for `sysdesign-drill`. Use these to check the candidate's answers and pick probes; do not reveal them during a drill.

### NFR → Tension Mapping
Use this to verify if the user's tension identification is correct. Do not show it.

| NFR | Tension | Trap to watch for |
|-----|---------|------------------|
| Low latency | Latency vs Consistency | Claims both are achievable with caching - not under partition |
| High availability | Availability vs Consistency (CAP) | Reaches for Zookeeper - coordination is the opposite of availability |
| Strong consistency / exact counts | Consistency vs Availability | Proposes Cassandra for strong consistency - it's eventual by default |
| Read-heavy (100:1) | Read throughput vs Write cost | Adds cache without addressing invalidation tradeoff |
| Write-heavy | Write throughput vs Durability | Forgets async writes risk data loss |
| Exactly-once | Exactly-once vs Performance | Doesn't acknowledge coordination cost |
| Cache adoption | Consistency vs Hit Rate | Doesn't name which cache strategy (aside/through/back) and what each accepts |

### Component Deep-Dive Prompts (Phase 3 Half B)
Use this to pick the right internals to probe for the component the user picked (or that you picked). Do not show this table.

| Component | Highest-yield probe |
|-----------|---------------------|
| Cache | Eviction policy as a tradeoff, not a config - LRU vs LFU vs TTL, and what each accepts. Cache stampede on hot-key expiry. |
| Message queue / log | Partition strategy, consumer rebalance, exactly-once vs at-least-once + idempotency, retention vs replay cost. |
| Primary KV / document store | Replication mode (sync/async), quorum reads, secondary index cost, hot-shard mitigation. |
| Relational DB | Index choice driven by access pattern, isolation level, vacuum/locking under write load. |
| Coordinator (ZK/etcd/Raft) | Quorum size, leader election cost, what happens during a leader change, why availability is bounded. |
| Search index | Inverted index update cost, near-real-time vs batch rebuild, recall vs precision vs freshness. |
| Ranker / ML scorer | Feature staleness, model serving latency budget, fallback path on model timeout. |
| Rate limiter | Global vs local state, token bucket vs sliding window, what exactness costs in coordination. |
| Stream processor | Watermarks, late events, exactly-once via checkpointing + idempotent sinks, state size growth. |
| Load balancer / gateway | Health check granularity, connection draining, retry storms, circuit breaking. |

### Capacity Sanity Checks (Phase 2.5 Block A)
Use this to verify the user's BOTE math is in the right zip code. Do not show this table.

| Quantity | Rough sanity range | Red flag if user says |
|----------|--------------------|-----------------------|
| Single-machine NIC | ~10–25 Gbps | "1 TB/sec on one box" |
| Single SSD throughput | ~500 MB/s sustained | "millions of disk seeks/sec on one disk" |
| Single Redis instance | ~100K ops/sec/core | "1M ops/sec from one Redis" |
| Single Kafka partition | ~10 MB/sec | "one partition handles 1 GB/sec" |
| RTT in-region | ~1 ms | "in-region call is 100 ms" |
| RTT cross-region | ~50–150 ms | "cross-region is 1 ms" |
| Daily active → peak QPS | ~ DAU × actions/day / 86400 × 3 (peak factor) | Skips the peak factor entirely |

### Dominant Layer by Question Type
Use this to know where to focus your Phase 2 and 3 probing.

| Question | Dominant Layer | What to probe hardest |
|----------|---------------|----------------------|
| Ads / Attribution / Measurement | L2/L3 | Constraints ARE the answer - push on late events, duplicates, unobservable causality |
| Feed / Timeline | L3/L4 | Push on the fan-out tradeoff - celebrity accounts break fan-out-on-write |
| Fraud Detection | L1/L2/L3 | Push on false positive cost - it's a business decision, not a technical one |
| Notification | L3/L4 | Push on exactly-once vs at-least-once and what idempotency that requires |
| Analytics Dashboard | L3/L4 | Push on correctness vs latency - Lambda vs Kappa is the real question |
| Rate Limiter | L4/L5 | Push on global vs local state and what exactness costs |
| Distributed Cache | L4/L5 | Push on eviction policy as a tradeoff decision, not a config choice |
| URL Shortener | L4/L5 | Simpler - push on read/write split and hash collision |
| Search | L3/L4 | Push on recall vs precision vs freshness and which the product requires |
