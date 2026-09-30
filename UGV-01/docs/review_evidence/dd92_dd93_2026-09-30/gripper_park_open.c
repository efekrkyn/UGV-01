#define main baseline_core_main
#include "../../../tests/lite_core_test.c"
#undef main
int main(void){
 Rig r;rig_parked(&r);arm(&r);
 const uint8_t out[][2]={{UGV_ARM_STOW,UGV_ARM_LIFT},{UGV_ARM_LIFT,UGV_ARM_UP},{UGV_ARM_UP,UGV_ARM_READY}};
 for(int i=0;i<3;i++){assert(arm_cmd(&r,out[i][0],out[i][1],65535));drive(&r,0,0,3000);}
 claw(&r,0);drive(&r,0,0,600);assert(claw_there(&r,UGV_GRIP_OPEN_CDEG));
 handshake(&r,100);assert(!r.out.act_en && r.c.arm_limp);
 /* Operator parks arm by hand; old claw target is still OPEN, even if the operator closed it by hand to fit. */
 assert(park(&r,0x5678));arm(&r);run(&r,200);
 printf("manual-park then re-arm: STOW=%d claw_target=%d claw_pos=%d claw_PWM=%u ACT_EN=%d\n",at_pose(&r,UGV_ARM_STOW),r.c.servo.target_cdeg[UGV_SERVO_GRIPPER],r.c.servo.pos_cdeg[UGV_SERVO_GRIPPER],r.out.servo_us[UGV_SERVO_GRIPPER],r.out.act_en);
 assert(at_pose(&r,UGV_ARM_STOW)&&r.out.act_en&&r.out.servo_us[UGV_SERVO_GRIPPER]==2167);return 0;
}
