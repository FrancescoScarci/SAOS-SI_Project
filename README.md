La seguente applicazione fornisce all'utente un sito web nel quale caricare una proposta progettuale in formato .txt. Sul caricamento vengo effettuate delle verifiche in cui controllare se il file che si sta caricando è realmente un file .txt
 e non un tipo di file differente. In più è effettuato un controllo sulla dimensione del file (non deve superare i 3 mb). In più vi è un controllo sul contenuto nella quale vengono rimossi eventuali tag javascript per evitare possibili attacchi.

 Per accedere all'applicazione bisogna autenticarsi facendo login attraverso le proprie credenziali github utilizzando un login federato con OAuth2.

Per la realizzazione del progetto si è utilizzato Flask che è un micro framework web scritto in Python. È classificato come microframework perché non richiede strumenti o librerie particolari.

Si è preparato l'ambiente di lavoro installando python e usando come IDE Visual Studio Code ed installando le libreire necessarei

Crea un nuovo ambiente virtuale:
``` bash
python -m venv venv
.venv\Scripts\activate
```

Installa Flask e Authlib:
``` bash
pip install flask authlib
```
