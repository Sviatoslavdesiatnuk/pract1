package TrafficControl {
    item def TimerExpired;

    state def TrafficLight {
        entry; then Red;

        state Red;
        state Yellow;
        state Green;

        transition from Red to Green    { accept TimerExpired; }
        transition from Green to Yellow { accept TimerExpired; }
        transition from Yellow to Red   { accept TimerExpired; }
    }
}