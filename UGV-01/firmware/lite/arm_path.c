#include "arm_path.h"

#include <stdlib.h>

static int is_edge(uint8_t a, uint8_t b) {
    for (int e = 0; e < UGV_ARM_EDGES; ++e)
        if ((UGV_ARM_EDGE[e][0] == a && UGV_ARM_EDGE[e][1] == b) || (UGV_ARM_EDGE[e][0] == b && UGV_ARM_EDGE[e][1] == a))
            return 1;
    return 0;
}

void ugv_arm_path_init(UgvArmPath *a) {
    a->from = a->to = UGV_ARM_STOW;
    a->frac = a->target = 65535;
}

int ugv_arm_path_at_node(const UgvArmPath *a, uint8_t node) {
    return (a->frac == 65535 && a->to == node) || (a->frac == 0 && a->from == node);
}

int ugv_arm_path_command(UgvArmPath *a, uint8_t from, uint8_t to, uint16_t target) {
    if (from >= UGV_ARM_POSES || to >= UGV_ARM_POSES) return 0;
    if (from == to) {  /* hold at a node */
        if (!ugv_arm_path_at_node(a, from)) return 0;
        a->from = a->to = from;
        a->frac = a->target = 65535;
        return 1;
    }
    if (!is_edge(from, to)) return 0;
    if (from == a->from && to == a->to) {
        a->target = target;
    } else if (from == a->to && to == a->from) {  /* reverse: same line, fraction mirrored */
        a->from = from;
        a->to = to;
        a->frac = (uint16_t)(65535 - a->frac);
        a->target = target;
    } else if (ugv_arm_path_at_node(a, from)) {
        a->from = from;
        a->to = to;
        a->frac = 0;
        a->target = target;
    } else {
        return 0;
    }
    return 1;
}

void ugv_arm_path_tick(UgvArmPath *a, uint32_t dt_ms) {
    int32_t span = 0;
    for (int j = 0; j < UGV_ARM_JOINTS; ++j) {
        const int32_t d = abs(UGV_ARM_POSE_CDEG[a->to][j] - UGV_ARM_POSE_CDEG[a->from][j]);
        if (d > span) span = d;
    }
    if (!span) {
        a->frac = a->target;
        return;
    }
    /* ponytail: whole fraction steps (truncated); the path still ends exactly at the target */
    const int32_t step = (int32_t)((int64_t)UGV_ARM_RATE_CDEG_S * dt_ms * 65535 / 1000 / span);
    const int32_t error = (int32_t)a->target - a->frac;
    a->frac = (uint16_t)(a->frac + (error > step ? step : error < -step ? -step : error));
}

void ugv_arm_path_cdeg(const UgvArmPath *a, int32_t cdeg[UGV_ARM_JOINTS]) {
    for (int j = 0; j < UGV_ARM_JOINTS; ++j) {
        const int32_t p0 = UGV_ARM_POSE_CDEG[a->from][j], p1 = UGV_ARM_POSE_CDEG[a->to][j];
        cdeg[j] = p0 + (int32_t)((int64_t)(p1 - p0) * a->frac / 65535);
    }
}
