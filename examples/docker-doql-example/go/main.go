package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
)

type Response struct {
	Message   string `json:"message"`
	Service   string `json:"service"`
	Language  string `json:"language"`
	Version   string `json:"version"`
	DBHost    string `json:"db_host"`
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	response := Response{
		Message:  "OK",
		Service:  os.Getenv("SERVICE_NAME"),
		Language: "Go",
		Version:  "1.21",
		DBHost:   os.Getenv("DB_HOST"),
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func apiHandler(w http.ResponseWriter, r *http.Request) {
	response := Response{
		Message:  "Hello from Go service!",
		Service:  os.Getenv("SERVICE_NAME"),
		Language: "Go",
		Version:  "1.21",
		DBHost:   os.Getenv("DB_HOST"),
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func main() {
	port := "8080"
	if p := os.Getenv("PORT"); p != "" {
		port = p
	}
	
	http.HandleFunc("/health", healthHandler)
	http.HandleFunc("/api", apiHandler)
	
	fmt.Printf("Go service listening on port %s\n", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
