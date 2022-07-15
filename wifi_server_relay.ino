#include <WiFi.h>
#include <WebServer.h>

int relayInput = 2; // the input to the relay pin

char wifiSsid[] = "WIFI_SSID";
char wifiPass[] = "WIFI_PASSWORD";
char authCode[] = "YOUR_SECRET_HEADER_KEY";
int  serverPort = PORT;

int relayActivateMs = 3000; //Miliseconds to activate relay

boolean debugOutput = false;
int serialBauds = 115200;

WebServer server(serverPort);

void setup() {
  pinMode(relayInput, OUTPUT); // initialize pin as OUTPUT
  digitalWrite(relayInput, LOW);

  if (debugOutput) {
    Serial.begin(serialBauds);
  }
  WiFi.begin(wifiSsid, wifiPass);  //Connect to the WiFi network

  while (WiFi.status() != WL_CONNECTED) {  //Wait for connection
    delay(500);
    if (debugOutput) {
      Serial.println("Waiting to connect…");
    }
  }

  if (debugOutput) {
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  }

  server.on("/", handleRootPath);    //Associate the handler function to the path

  //ask server to track these headers
  const char * headerkeys[] = {"AuthCode"} ;
  size_t headerkeyssize = sizeof(headerkeys) / sizeof(char*);
  server.collectHeaders(headerkeys, headerkeyssize );
  server.begin();                    //Start the server
  if (debugOutput) {
    Serial.println("Server listening");
  }
}

void loop() {
  server.handleClient();         //Handling of incoming requests
}

void handleRootPath() {
  if (server.hasHeader("AuthCode") && server.header("AuthCode") == authCode) {
    server.send(200, "text/plain", "Opening door ...");
    digitalWrite(relayInput, HIGH); // turn relay on
    delay(relayActivateMs);
    digitalWrite(relayInput, LOW); // turn relay off
    if (debugOutput) {
      Serial.print('Opening door');
    }
  } else {
    server.send(400, "text/plain", "Not authorized");
    if (debugOutput) {
      Serial.print('Permission denied');
    }
  }
}