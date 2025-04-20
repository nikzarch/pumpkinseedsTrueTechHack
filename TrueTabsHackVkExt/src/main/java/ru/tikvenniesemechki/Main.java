package ru.tikvenniesemechki;

import ru.tikvenniesemechki.service.MassageHandlerService;

public class Main {
    public static void main(String[] args) {
        MassageHandlerService massageHandlerService = new MassageHandlerService();
        massageHandlerService.startMassageHandler();
    }
}