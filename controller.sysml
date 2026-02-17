package AI_Home {

    item def Click;

    state def LightSwitchLogic {

        entry; then Off;

        state Off;
        state On;


        transition Off_to_On from Off to On {
            accept Click;
        }

        transition On_to_Off from On to Off {
            accept Click;
        }
    }
}