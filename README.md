# Bot_One
Bot_One is a Twitch bot built using the TwitchIO API


il bot é pensato per funzionare con GNU/Linux, puoi usarlo nativamente sul tuo PC oppure su una VM (macchina virtuale)

ti consiglio di usare una VM

## installazione VM

Creazione macchina virtuale con VirtualBox

1) installa VirtualBox da virtualbox.org

2) scarica debian-testing-amd64-netinst.iso da https://cdimage.debian.org/cdimage/daily-builds/daily/arch-latest/amd64/iso-cd/

3) Apri VirtualBox e premi Ctrl+N per creare una nuova VM

4) dai un nome alla tua VM (ad esempio debian_bot), scegli il percorso dove vuoi salvarla, seleziona la iso di Debian scaricata al punto 2) , spunta "Salta l'installazione non supervisionata" e conferma con "Fine"

5) avvia la VM appena creata

6) seleziona "install" e premi invio, puoi muoverti nei menú con le "frecce" e "tab", selezionare con "spazio" e confermare con "invio", segui le istruzioni a schermo (se hai dubbi lascia le scelte di default) per le opzioni di localizzazione, hostname, password di root, crea un nuovo utente chiamato "bot", partizionamento disco e proxy.

7) nella selezione software togli tutti gli asterischi (usando la barra spaziatrice) e lascia solo "Standard System Utilities", aggiungi "SSH server" se vorrai collegarti in futuro per gestire la VM tramite SSH, seleziona continua per confermare, installa GRUB su /dev/sda e continua per riavviare

8) dopo il riavvio vai sulla finestra della VM e nel menú seleziona

    "Dispositivi" -> "Lettori ottici"  -> "Rimuovi disco dal lettore virtuale"
  
    "Dispositivi" -> "Inserisci l'immagine del CD delle Guest Additions..."



9) loggati come root alla VM e dai i seguenti comandi:
```bash
mount /dev/cdrom
sh /media/cdrom/VBoxLinuxAdditions.run
mkdir /debian_bot/
chmod 777 /debian_bot/
```

10) crea una cartella sul tuo computer da condividere con la VM, ad esempio "debian_bot", vai sulla finestra della VM e nel menú seleziona:
"Dispositivi" -> "Cartelle condivise" -> "Impostazioni cartelle condivise..."
clicka sul "+" per aggiungere la cartella condivisa appena creata, seleziona il percorso della cartella condivisa ("debian_bot" nell'esempio di prima) e metti /debian_bot/ come punto di mount, spunta "montaggio automatico" e "rendi permanente", conferma e digita nel terminale della VM:
```bash
df -h | grep debian_bot
```
se visualizzi la condivisione appena creata vuol dire che é stata creata correttamente

11) loggati come root alla VM e aggiorna il sistema con il seguente comando:
```bash
apt update && apt -y upgrade && apt -y autoremove && apt clean
```
installa le dipendenze del bot:
```bash
apt install python3-venv python3-pip mpv yt-dlp espeak-ng espeak-ng-data
```
aggiungi l'utente "bot" al gruppo "vboxsf" con il comando:
```bash
usermod -aG vboxsf bot
```
riavvia con il comando:
```bash
reboot
```
loggati come utente "bot" , crea l'ambiente python ed installa le librerie TwitchIO con i seguenti comandi:
```bash
python3 -m venv bot
source bot/bin/activate
pip install -U twitchio
```
copia la cartella bot_one_1.0.x dentro la cartella condivisa "debian_bot" sul tuo PC, ora dovresti poter leggerne il contenuto nella diretory /debian_bot/ della VM

installazione VM terminata


## avvio del bot
per avviare lo script del bot_one loggati come utente "bot" alla VM e attiva l'ambiente python con il seguente comando:
```bash
source /home/bot/bot/bin/activate
```
e spostati nella diretory debian_bot:
```bash
cd /debian_bot/
ls -la
```
puoi avviare lo script python con:
```bash
python3 nome_script.py
```
se non hai un token guarda la guida alla generazione di un token con Token Generator su https://twitchio.dev/en/stable/quickstart.html 

## configurazione del bot
al primo avvio del bot partirá la configurazione automatica che creerá il file config.json, se vuoi puoi modificare manualmente le impostazioni puoi editare il file config.json contenuto nella directory del bot

    "token": "...",              <- metti qui il tuo token Twitch
    "prefix": ["!"],             <- metti qui il prefisso dei comandi oppure lascia "!"
    "initial_channels": ["..."]  <- metti qui il nome del canale Twitch a cui collegare il bot


## come usare il bot
dopo aver collegato il bot al canale scrivi "!comandi" nella chat di Twitch

