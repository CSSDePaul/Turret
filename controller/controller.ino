char data=0;
int LEFT = 6;                 
int RIGHT = 8;
int FIRE = 10;

void setup()
{
  Serial.begin(9600);
  pinMode(LEFT, OUTPUT);      
  pinMode(RIGHT, OUTPUT);
  pinMode(FIRE, OUTPUT);
  digitalWrite(LEFT,HIGH);
  digitalWrite(RIGHT,HIGH);
  digitalWrite(FIRE,HIGH);
}

void loop()
{
  if(Serial.available() > 0)
  {
    data = Serial.read();
    if(data == 'L')
    {
        digitalWrite(LEFT,LOW);
        delay(20);
        digitalWrite(LEFT,HIGH); 
    }
    if(data == 'R')
    {
        digitalWrite(RIGHT,LOW);
        delay(20);
        digitalWrite(RIGHT,HIGH);  
    }
    if(data == 'F')
    {
        digitalWrite(FIRE,LOW);
        delay(100);
        digitalWrite(FIRE,HIGH);
    }
  }
}
