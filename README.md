# cat_detector

### Problemstellung
Unsere neue Nachbarskatze kackt gerne under mein Velo, da es dort trocken ist. Leider passiert es manchmal dass man im Dunklen dann da reinsteht. Mein Ziel war es also den Platz als Toilette möglichst unattraktiv zu machen:



https://github.com/user-attachments/assets/32f9e533-0596-4e68-b20b-68eaa74434a3



#### Katzenerkennung
Daher habe ich einen Raspi 5 mit einer billigen Nachtsichtkamera und einem yolov11 object detection model kombiniert, um auf eine Katze in dieser Region reagieren zu können.

<img width="640" height="480" alt="cat_20260313131011_boxes" src="https://github.com/user-attachments/assets/30e507d2-3207-4cb2-8aa6-4571ef589131" />

**Code - simillar to [[Yolov11 on Raspberry Pi]]** -> im Repo

- additionally imports gpizero and turns servo 5x from 30 to 120° when something is detected - activates water sprayer


#### Wassersprüher mit Servo

<img width="4096" height="3072" alt="IMG_20260316_124812433" src="https://github.com/user-attachments/assets/4bd526f5-ee63-4c19-bbd3-25d1d21b13cb" />

CAD Form - ist mit 6° Neigungswinkel eingebettet

<img width="826" height="693" alt="Pasted image 20260311150058" src="https://github.com/user-attachments/assets/be5f6f5e-b57d-438c-86ca-9ba69ea35902" />

- Beide Boxen werden übereinander gelegt, Feder und kürzerer Hebelarm helfen, damit Servo genug Moment hat
- TODO evtl. Stärkeres Netzteil mit mehr Leisung für Servo - Zwischenlösung mit Feder, damit Servo genug Kraft hat, um den Spritzer gut zu bedienen

#### fertige Ansicht

<img width="3072" height="4096" alt="IMG_20260316_124747241" src="https://github.com/user-attachments/assets/2e0c859a-4a48-4231-8128-40d6cb39cb81" />


#### Schaltplan
- mit zwei Netzadaptern
<img width="1280" height="720" alt="maxresdefault-3866904133 1" src="https://github.com/user-attachments/assets/26d1a45a-944d-46dd-b801-c026a3108d66" />



### Praxistest
- Katzen sehen den Wasserstrahl im Dunklen nicht
- Änderung, damit Katze 2mal in Folge erkannt werden muss, damit Servo ausgelöst wird
- funktioniert gut, hatte mehrere Videos - vor allem laufem Katzen noch durch wenn es nur auslöst, wenn es zwei mal in Folge auslöst. Doch sie bleiben nicht mehr stehen im Hellen.



- manchmal auch als Hund erkannt -> auch bei anderen Tieren in Object classes auslösen: 
<img width="640" height="480" alt="cat_20260314020839_boxes" src="https://github.com/user-attachments/assets/c3b52baa-9def-4f3e-b943-04ac98eca407" />

##### andere Tiere
Waschbär - der gerade vom Wildhüter gesucht wird

<img width="640" height="480" alt="cat_20260411231746_boxes" src="https://github.com/user-attachments/assets/9d74e703-c090-4d43-8762-56f822297964" />

Fuchs

<img width="640" height="480" alt="cat_20260418035333_boxes" src="https://github.com/user-attachments/assets/b65d3a7a-e293-44f5-ac78-82385b44e9f2" />


