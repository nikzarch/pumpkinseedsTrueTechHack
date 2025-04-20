package logic

import (
	"mtctruetechhack/config"
	"net/smtp"
	"strconv"
)

type MailRequest struct {
	To      string `json:"to"`
	Subject string `json:"subject"`
	Body    string `json:"body"`
}

func SendMail(mailReq MailRequest) error {
	from := config.SMTPUser
	password := config.SMTPPasswd
	smtpHost := config.SMTPHost
	smtpPort := config.SMTPPort

	msg := []byte("To: " + mailReq.To + "\r\n" +
		"Subject: " + mailReq.Subject + "\r\n\r\n" +
		mailReq.Body + "\r\n")

	auth := smtp.PlainAuth("", from, password, smtpHost)
	return smtp.SendMail(smtpHost+":"+strconv.Itoa(smtpPort), auth, from, []string{mailReq.To}, msg)
}
