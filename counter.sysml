package CountingSystem {
    item def NextCommand;

    state def CounterLogic {
        entry; then Zero;
        state Zero;
        state One;
        state Two;
        state Three;

        transition Time1 from Zero to One   { accept NextCommand; }
        transition Time2 from One to Two    { accept NextCommand; }
        transition Time3 from Two to Three  { accept NextCommand; }
        transition Time4 from Three to Zero { accept NextCommand; }
    }
}