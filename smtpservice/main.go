package main

import (
	"github.com/joho/godotenv"
	"log"
	"mtctruetechhack/config"
	"mtctruetechhack/handlers"
	"net/http"
)

func main() {
	err := godotenv.Load(".env")
	if err != nil {
		log.Fatal("Error loading .env file")
	}
	config.LoadConfig()
	mux := http.NewServeMux()
	mux.HandleFunc("/sendMail", handlers.SendMailHandle)
	http.ListenAndServe(":8080", mux)
}
