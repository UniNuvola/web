package main

import (
	. "webgo/config"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/log"
	"github.com/gofiber/template/django/v2"
	"github.com/markbates/goth"
	"github.com/markbates/goth/providers/openidConnect"

	"webgo/routes"
)

var configs = map[string]string{
	"PORT":                 Config("PORT"),
	"CLIENT_ID":            Config("VAULT_CLIENT_ID"),
	"CLIENT_SECRET":        Config("VAULT_CLIENT_SECRET"),
	"CLIENT_CALLBACK":      Config("CLIENT_CALLBACK"),
	"CLIENT_DISCOVERY_URL": Config("CLIENT_DISCOVERY_URL"),

	// VAULT_CONF_URL = os.getenv('VAULT_CONF_URL')
	// SERVER_NAME = os.getenv('WEB_PUBLIC_URL')
	// LDAPSYNC_IP = os.getenv('LDAPSYNC_IP')
	// LDAPSYNC_PORT = os.getenv('LDAPSYNC_PORT')
}

func main() {
	log.SetLevel(log.LevelDebug)
	log.Debug("DEBUG ENABLED 🐛")

	PORT := configs["PORT"]
	log.Infof("SERVER PORT %s", PORT)

	engine := django.New("./templates", ".html")
	// engine.AddFunc("disablebutton", func(value interface{}) string {
	// 	if _, ok := value.(string); ok {
	//
	// 		return "disabled"
	// 	}
	// 	return ""
	// 	// if status == "synced" || status == "approved" {
	// 	// 	return ""
	// 	// }
	// 	//
	// 	// return "disabled"
	// })

	// Start a new fiber app
	app := fiber.New(
		fiber.Config{
			Views: engine,
		},
	)

	app.Static("/", "./static")
	// Set OpenIdConnect Provider
	openidProvider, err := openidConnect.New(
		configs["CLIENT_ID"],
		configs["CLIENT_SECRET"],
		configs["CLIENT_CALLBACK"],
		configs["CLIENT_DISCOVERY_URL"],
		// scopes
		"openid",
		"web",
	)
	if err != nil {
		log.Fatal("CANT INIT OIDC PROVIDER. ERROR %s", err)
	}

	goth.UseProviders(openidProvider)

	// Set Routes
	routes.SetRoutes(app)

	// Listen on PORT 300
	log.Fatal(app.Listen(":" + PORT))
}
