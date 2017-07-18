In dit project:
    Drivers
    *******
        3 soorten drivers
        *****************
            ABEL
            ****
                Om de waarden uit de vochtigheidssensoren uit te lezen, is er een ADC nodig die genoeg kanalen heeft om
                de signalen op te vangen. De ABEL driver initialiseert de i2c connectie en leest via read_voltage()
                de ontvangen spanning op de voorbestemde i2c adressen uit.
            ADA
            ***
                De licht en temperatuur sensor interfacen ook via het custom bord' i2c kanaal, maar door een andere ADC;
                Met de ADAFRUIT ads1115 worden mbv 4 kanalen, de temperatuur en 2 lichtsensoren uitgelezen. De AdaFruit_ADS1x1 is een oudere
                versie van de gebruikte driver (ADS1x15). ADS1x15 is niet alleen veel duidelijker, maar ook het initialiseren van de
                klasse is transparant zonder al te veel parameters te hoeven instellen.

            HX711
            *****
            De loadcell transleert geweicht via de pressure gauges op de aluminium balk naar een spanningsniveau.
            De metingen zijn echter in milivolts waardoor er nog een extra versterker toegevoegd moet worden.
            De HX711 versterkt de uitgelezen spanning uit de wheatstone bridge en zet het in digitale data om. De clk en dout interface op het
            bordje verzend de individuele bits op de clk flank en kan voor de volgende waarde opnieuw de versterking instellen.
            In tegenstelling tot de i2c interface van ABEL en ADA worden voor de clk en dout de GPIO pinnen van de Raspberry PI aangestuurd.


    Graphic BiLLy Billy
    *******************
            jsonrw
            ******
                Basis functionaliteit om de JSON strings uit een file te lezen en deze om te zetten in een lijst van dictionnaries
                alsook om de sensorwaarden te capteren en naar JSON strings om te zetten en op te slaan in een text bestand.

            Sensor
            ******
                In een poging om de sensoren interface zo duidelijk mogelijk te maken en toevoeging van extra sensoren te vergemakkelijken
                werden er individuele klassen gemaakt die op basis van de interface superklasse automatisch ingesteld kunnen worden.

            SensorManagager
            ***************
            Deze klasse houdt alle sensoren bij en biedt alle sensorwaarden in een lijst aan.
            Het bijhouden van alle sensoren in 1 klasse vergemakkelijkt het opvragen van de bijhorende JSON strings.

            vpython_pot
            ***********
            Als er een text bestand met json waarden beschikbaar is en deze string een 'values' entry heeft, dan kunnen de
            vochtigheidswaarden via vpython (2000) lib grafisch dmv bollen weergegeven worden.
            Het toewijzen van de sensoren aan het bolmodel verloopt via de respectievelijke kanalen waarop de sensoren op
            zijn aangeslotenn. (vb Sensor 1 = kanaal 1,bord 1 , sensor 8 = kanaal 8,bord1,  sensor 9 = kanaal 1,bord 2, senor 12 = kanaal 4, bord 2)

    Plotly_pot
    **********
            Omdat de raspberry pi zonder monitor geen data kan plotten, wordt er gebruik gemaakt van online dataplatform, plot.ly.
            De mogelijkheden die het platform aanbiedt, overtreft in sommige gevallen zelfs matplotlib o.a in de streaming functionaliteit.
            In dit ontwerp word de sensor data direct via een stream geupload en geplot in 12 verschillende grafieken.
            De data die in elke afzonderlijke grafiek wordt afgebeeld is afhankelijk van de max_point instelling, waardoor monitoring in een
            zekere mate begrensd wordt.



