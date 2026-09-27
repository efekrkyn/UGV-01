#ifndef UGV_ARM_PATH_H
#define UGV_ARM_PATH_H

#include <stdint.h>

#include "arm_graph.h"

/* N1 (M3 review): the arm's position on the swept pose graph. `frac` runs 0 (at pose `from`) .. 65535 (at pose
   `to`); a node is (n, n, 65535). Only edge moves are accepted, so all five joints stay on a straight line the
   CAD checked, whatever the MacBook sends and however many datagrams are lost. */
typedef struct {
    uint8_t from, to;
    uint16_t frac, target;
} UgvArmPath;

void ugv_arm_path_init(UgvArmPath *a);  /* at stow */
/* 1 = accepted: the same edge (new target), the reverse of it (back along the same line), or a new edge that
   starts at the node the arm is at; from == to holds at that node. Anything else is refused. */
int ugv_arm_path_command(UgvArmPath *a, uint8_t from, uint8_t to, uint16_t target);
void ugv_arm_path_tick(UgvArmPath *a, uint32_t dt_ms);  /* fastest joint at UGV_ARM_RATE_CDEG_S */
void ugv_arm_path_cdeg(const UgvArmPath *a, int32_t cdeg[UGV_ARM_JOINTS]);
int ugv_arm_path_at_node(const UgvArmPath *a, uint8_t node);

#endif
