package handlers

import (
	"encoding/json"
	"mtctruetechhack/logic"
	"net/http"
)

func SendMailHandle(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "POST is only allowed", http.StatusMethodNotAllowed)
		return
	}
	var req logic.MailRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Parse error", http.StatusBadRequest)
		return
	}
	err := logic.SendMail(req)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	w.Write([]byte("ok"))
}
