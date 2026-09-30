#define main baseline_tof_main
#include "../../../tests/vl53l0x_test.c"
#undef main
int main(void) {
 dev[0].present=dev[1].present=1;boot(&dev[0]);boot(&dev[1]);UgvTof tof[2];assert(start(tof)==2);
 const uint8_t statuses[]={4,6,9};
 for(int k=0;k<3;k++){uint16_t mm[2];sample_status(&dev[0],8190,statuses[k]);sample_status(&dev[1],8190,statuses[k]);ugv_tof_pair_poll(&bus,tof,1000+20*k,mm);printf("raw=%u invalid: driver=%u,%u\n",statuses[k],mm[0],mm[1]);assert(mm[0]==8190&&mm[1]==8190);}
 return 0;
}
