#define main baseline_core_main
#include "../../../tests/lite_core_test.c"
#undef main
static void route(Rig*r,const uint8_t e[][2],int n){for(int i=0;i<n;i++){assert(arm_cmd(r,e[i][0],e[i][1],65535));drive(r,0,0,3000);}}
int main(void){
 Rig r;rig_parked(&r);arm(&r);
 const uint8_t out[][2]={{UGV_ARM_STOW,UGV_ARM_LIFT},{UGV_ARM_LIFT,UGV_ARM_UP},{UGV_ARM_UP,UGV_ARM_READY}};
 const uint8_t home[][2]={{UGV_ARM_READY,UGV_ARM_UP},{UGV_ARM_UP,UGV_ARM_LIFT},{UGV_ARM_LIFT,UGV_ARM_STOW}};
 route(&r,out,3);claw(&r,0);drive(&r,0,0,600);assert(claw_there(&r,UGV_GRIP_OPEN_CDEG));
 claw(&r,1);drive(&r,0,0,600);printf("READY open->close: empty=%d closed=%d\n",r.c.grip_empty,claw_there(&r,0));
 route(&r,home,3);drive(&r,100,100,600);printf("READY grasp->stow: drive_allowed=%d empty=%d duties=%d,%d,%d,%d\n",lite_core_arm_allows_drive(&r.c),r.c.grip_empty,r.out.duty_permil[0],r.out.duty_permil[1],r.out.duty_permil[2],r.out.duty_permil[3]);assert(all(&r,1));
 drive(&r,0,0,600);route(&r,out,3);claw(&r,0);drive(&r,0,0,600);assert(arm_cmd(&r,UGV_ARM_READY,UGV_ARM_REACH_LOW,65535));drive(&r,0,0,3000);
 claw(&r,1);drive(&r,0,0,600);assert(!r.c.grip_empty);assert(arm_cmd(&r,UGV_ARM_REACH_LOW,UGV_ARM_READY,65535));drive(&r,0,0,3000);route(&r,home,3);drive(&r,100,100,600);assert(all(&r,0));
 printf("REACH_LOW grasp before reset: empty=%d drive_allowed=%d\n",r.c.grip_empty,lite_core_arm_allows_drive(&r.c));
 lite_core_init(&r.c,KEY,sizeof KEY,r.now);r.left=r.right=0;handshake(&r,60);assert(park(&r,0x5678));arm(&r);drive(&r,100,100,600);
 printf("after watchdog+arm-park (no claw open): empty=%d drive_allowed=%d duties=%d,%d,%d,%d\n",r.c.grip_empty,lite_core_arm_allows_drive(&r.c),r.out.duty_permil[0],r.out.duty_permil[1],r.out.duty_permil[2],r.out.duty_permil[3]);assert(all(&r,1));return 0;
}
