package config

import (
	"os"
	"strconv"
)

var SMTPHost, SMTPUser, SMTPPasswd string
var SMTPPort int

func LoadConfig() {
	SMTPHost = os.Getenv("SMTP_HOST")
	SMTPUser = os.Getenv("SMTP_USER")
	SMTPPasswd = os.Getenv("SMTP_PASSWD")
	SMTPPort, _ = strconv.Atoi(os.Getenv("SMTP_PORT"))
}
