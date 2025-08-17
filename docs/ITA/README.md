# PDF Duplicate Finder

## Panoramica
PDF Duplicate Finder è un'applicazione progettata per aiutarti a trovare e gestire i file PDF duplicati nel tuo sistema. Utilizza algoritmi avanzati di hashing per identificare i PDF duplicati, anche se hanno nomi o metadati diversi.

## Caratteristiche

### 1. Rilevamento Duplicati
- Scansiona le directory alla ricerca di file PDF duplicati
- Confronta i file utilizzando l'hashing dei contenuti
- Visualizza un confronto affiancato dei potenziali duplicati

### 2. Visualizzatore PDF
- Visualizzatore PDF integrato con controlli di zoom e navigazione
- Visualizza anteprime delle pagine per una navigazione rapida
- Cerca all'interno dei documenti PDF

### 3. Gestione File
- Segna i file per l'eliminazione o lo spostamento
- Anteprima dei file prima di intraprendere azioni
- Elaborazione in batch di più file

### 4. Personalizzazione
- Regola la sensibilità del confronto
- Imposta directory di scansione personalizzate
- Configura filtri ed esclusioni di file

## Guida all'Uso

### Prerequisiti
- Python 3.8 o superiore
- Pacchetti Python richiesti (installabili tramite `pip install -r requirements.txt`)

### Installazione
1. Clona il repository
2. Installa le dipendenze: `pip install -r requirements.txt`
3. Avvia l'applicazione: `python main.py`

## Utilizzo

### Scansione dei Duplicati
1. Fai clic su "Aggiungi Directory" per selezionare le cartelle da scansionare
2. Regola le impostazioni di confronto se necessario
3. Fai clic su "Avvia Scansione" per iniziare la ricerca dei duplicati
4. Rivedi i risultati nella finestra principale

### Gestione dei Duplicati
- Seleziona i file per visualizzare le anteprime
- Usa i pulsanti di azione per gestire i file:
  - Elimina i file selezionati
  - Sposta i file in un'altra posizione
  - Apri i file nel visualizzatore integrato

## Scorciatoie da Tastiera

| Tasti | Azione |
|-------|--------|
| Ctrl+O | Apri directory |
| Ctrl+P | Apri visualizzatore PDF |
| F1     | Visualizza documentazione |
| Canc   | Elimina i file selezionati |
| F5     | Aggiorna la vista |

## Supporto

Per supporto, apri un'issue sul nostro [repository GitHub](https://github.com/Nsfr750/PDF_finder).

## Licenza

Questo progetto è concesso in licenza con licenza GPLv3 - vedi il file [LICENSE](LICENSE) per i dettagli.

## Contributi

I contributi sono ben accetti! Si prega di leggere le nostre [linee guida per i contributi](CONTRIBUTING.md) prima di inviare pull request.
