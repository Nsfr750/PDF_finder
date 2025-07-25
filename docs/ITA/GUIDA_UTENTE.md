# PDF Duplicate Finder - Guida Utente

## Indice
1. [Introduzione](#introduzione)
2. [Installazione](#installazione)
3. [Panoramica dell'Interfaccia](#panoramica-dellinterfaccia)
4. [Ricerca dei Duplicati](#ricerca-dei-duplicati)
5. [Gestione dei Risultati](#gestione-dei-risultati)
6. [Utilizzo del Visualizzatore PDF](#utilizzo-del-visualizzatore-pdf)
7. [Funzionalità Avanzate](#funzionalità-avanzate)
8. [Risoluzione dei Problemi](#risoluzione-dei-problemi)
9. [Domande Frequenti](#domande-frequenti)

## Introduzione
Benvenuto in PDF Duplicate Finder! Questa guida ti aiuterà a sfruttare al massimo le funzionalità dell'applicazione per trovare e gestire i file PDF duplicati sul tuo sistema.

## Installazione

### Requisiti di Sistema
- Windows 10/11, macOS 10.15+ o Linux
- Python 3.8 o superiore
- Minimo 4GB di RAM (8GB consigliati)
- 100MB di spazio libero su disco

### Installazione Passo-Passo
1. Scarica l'ultima versione da GitHub
2. Estrai l'archivio nella cartella preferita
3. Apri un terminale/prompt dei comandi nella directory estratta
4. Esegui: `pip install -r requirements.txt`
5. Avvia l'applicazione: `python main.py`

## Panoramica dell'Interfaccia

### Finestra Principale
- **Barra dei Menu**: Accesso a tutte le funzioni dell'applicazione
- **Barra degli Strumenti**: Accesso rapido alle azioni comuni
- **Elenco Directory**: Mostra le cartelle in fase di scansione
- **Pannello Risultati**: Visualizza i duplicati trovati
- **Pannello Anteprima**: Mostra l'anteprima dei file selezionati
- **Barra di Stato**: Mostra lo stato corrente e i progressi

### Navigazione
- Usa il menu Visualizza per mostrare/nascondere i pannelli
- I menu contestuali (tasto destro) offrono opzioni aggiuntive
- Trascina e rilascia i file PDF direttamente nella finestra

## Ricerca dei Duplicati

### Scansione di Base
1. Fai clic su "Aggiungi Directory" e seleziona una cartella da scansionare
2. Regola le impostazioni di scansione se necessario
3. Fai clic su "Avvia Scansione"
4. Visualizza i risultati nella finestra principale

### Opzioni di Scansione Avanzate
- **Confronto Contenuti**: Confronta il contenuto effettivo dei PDF
- **Confronto Metadati**: Controlla le proprietà del documento
- **Filtro Dimensione File**: Ignora i file al di fuori di determinati intervalli di dimensione
- **Filtro Intervallo Date**: Concentrati sui file modificati in date specifiche

## Gestione dei Risultati

### Lavorare con i Duplicati
- Seleziona i file per visualizzare un confronto dettagliato
- Usa le caselle di controllo per contrassegnare i file per le azioni
- Usa il tasto destro del mouse per le opzioni del menu contestuale

### Azioni Disponibili
- **Elimina**: Rimuovi i file selezionati
- **Sposta**: Rilocalizza i file in una nuova posizione
- **Apri**: Visualizza i file nell'applicazione predefinita
- **Escludi**: Aggiungi file/cartelle all'elenco delle esclusioni

## Utilizzo del Visualizzatore PDF

### Navigazione
- Usa i tasti freccia o i pulsanti a schermo per navigare tra le pagine
- Inserisci il numero di pagina per passare direttamente a una pagina specifica
- Usa i controlli di zoom per regolare la visualizzazione

### Funzionalità
- **Ricerca**: Trova testo all'interno del documento
- **Visualizzazione Anteprime**: Naviga utilizzando le anteprime delle pagine
- **Ruota**: Ruota le pagine per una migliore visualizzazione
- **Segnalibri**: Salva e gestisci i segnalibri

## Funzionalità Avanzate

### Elaborazione in Batch
- Elabora più file contemporaneamente
- Crea sequenze di azioni personalizzate
- Salva e carica profili di elaborazione

### Automazione
- Pianifica scansioni regolari
- Imposta regole di pulizia automatica
- Esporta i risultati della scansione in vari formati

## Risoluzione dei Problemi

### Problemi Comuni
- **Prestazioni Lente**: Prova a scansionare directory più piccole o regola le impostazioni di confronto
- **File Non Trovati**: Controlla i permessi dei file e le esclusioni
- **Blocchi dell'Applicazione**: Aggiorna all'ultima versione e verifica i requisiti di sistema

### File di Log
- I log dell'applicazione sono memorizzati in `logs/`
- Attiva la modalità debug per una registrazione dettagliata
- Includi i log quando segnali problemi

## Domande Frequenti

### Generali
**D: I miei dati vengono inviati a server esterni?**
R: No, tutta l'elaborazione avviene localmente sul tuo computer.

**D: Quali tipi di file sono supportati?**
R: Attualmente sono supportati solo i file PDF.

### Tecniche
**D: Come funziona il rilevamento dei duplicati?**
R: Utilizziamo una combinazione di hashing dei file e analisi del contenuto per identificare i duplicati.

**D: Posso recuperare i file eliminati?**
R: I file eliminati tramite l'applicazione vengono spostati nel cestino di sistema e possono essere ripristinati da lì.

### Supporto
**D: Come segnalo un bug?**
R: Apri una segnalazione sul nostro repository GitHub con i passaggi dettagliati per riprodurre il problema.

**D: Dove posso richiedere una nuova funzionalità?**
R: Le richieste di nuove funzionalità possono essere inviate tramite le issue di GitHub o il nostro forum della community.

---
*Ultimo aggiornamento: 25 Luglio 2025*
