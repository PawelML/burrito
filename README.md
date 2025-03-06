1. **Interfejs Użytkownika**:
- Aplikacja posiada trzy główne szablony HTML: `index.html`, `akcje.html`, `sku.html`
- `index.html` zawiera formularz do wyszukiwania produktów, gdzie użytkownik może filtrować po Gru_4 lub wyszukać produkt po 'opisie' lub nr_katalog. Tabele można sortować klikając w wybraną nazwę kolumny. Checkbox po lewej stronie umożliwia dodawanie poszczególnych indeksów do 'Konkursu' - otwiera się 'koszyk' po prawej stronie w któym zarządzamy indeksami dodawanymi do konkursu oraz towrzymy lub aktualizujemy poszczególną konkurs.
- `competition_hisotry.html` zawiera wszystkie konkursy, które zostały utworzone. Checkbox koło nazwy konkursu umożliwia zmiane statusu aktywny / nieaktywny. Zaznaczenie checkboxa oznacza, że dane z konkursami będą wysyłane do drugiej grupy odbiorców (z założenia do DK lub RKS). W przypadku gdy checkbox nie jest zaznaczony e-mail trafia jedynie do operatora. Niebieski przycisk umożliwia wysłanie konkursu do operatora. Zielony przycisk umożliwia wykoanie kopii danego konkursu - te same indkesy, ale możliwość zmiany nazwy, czasu obowiązywania konkursu. Czerwony przycisk usuwa konkurs. Tabelka zawiera wszystkie indeksy wchodzące w skład konkursu, nazwę konkursu, datę rozpoczęcia, datę zakończenia, status oraz nazwę operatora. 
- `budget_planing.html` umożliwia załadowanie budżetów za pomocą pliku excel. Umożliwia również podgląd już instniejących budżetów i zmianę ich parametrów.

2. **Skrypty**:
- `plan_c_sender.py` - skrypt służący do wysyłania maili z planem C. Uruchamiany za pomocą pliku plan_c_sender.bat
- `extract_konkurs.py` - skrypt w formie testowej (nieużywany)służący do pobierania maili z konkursami, który następnie umożliwia wyciągniecie wszystkich nr katalogowych z pliku pdf załączonego do maila.
- `mail_to_dk.py` - skrypt służący do wysyłania maili do DK. Uruchamiany za pomocą pliku run_scripts.bat
- `mail_do_rks.py` - skrypt służący do wysyłania maili do RKS. Uruchamiany za pomocą pliku run_scripts.bat
- `mail_to_virtuemart.py` - skrypt służący do wysyłania maili do Tomasz Wirta z podsumowaniem konkursów. Uruchamiany za pomocą pliku run_scripts.bat
- `script_to_operator.py` - skrypt służący do wysyłania maili do operatora z konkursami. Uruchamiany w aplikacji. Celem skryptu jest manualne wysłanie wyników danego konkursu do operatora, nawet jeżeli konkurs pochhodzi z poprzedniego miesiąca.

3. **Baza Danych**:
- Aplikacja łączy się z bazą danych SQL Server o nazwie "KONKURSY" zawierającą następujące tabele:
- [all_ind] zawiera wszystkie indeksy dostępne w ERP Optima
- [budgets_plan_C] zawiera budżety dla planu "C"
- [konkurs_wyniki] zawiera wyniki konkursów. Tabela jest odświeżana raz dziennie przez prodcedure [loadToKonkursy_wyniki]
- [prowadzone_konkursy] zawiera wszystkie konkursy wraz z ich parametrami

***Procedury***:
[loadToAll_ind]- zasila dane do tabeli [all_ind]
[load_T1_bez_brakow_once] - zasila dane do tabeli [konkurs_wyniki]

4. **Logowanie**:
- Aplikacja wymaga logowania podczas uruchamiania, do aplikacji jest przypisany jeden użytkownik o loginie 'admin'.'

## Technologie
- Backend: Python z frameworkiem Flask
- Frontend: HTML, CSS, JavaScript, jQuery, Bootstrap
- Baza danych: SQL Server

## Funkcjonalności

### Wyszukiwanie i Filtrowanie
- Zaawansowane opcje wyszukiwania produktów po różnych kryteriach.
- Dynamiczne filtrowanie wyników w czasie rzeczywistym.

### Zarządzanie Konkursami
- Tworzenie, edycja i usuwanie Konkursów.
- Przypisywanie produktów do konkursu.
- Wgrywanie budżetów dla konkursów za pomocą pliku excel i edycja budżetów za pomocą tabeli.

### Wysyłanie danych z wynikami konkursów mailowo
- Emaile są wysyłane raz dziennie z rana za pomocą ustawionego automatu w programie 'System Scheduler'. W zapytaniach SQL wewnątrz skryptów zawarty jest mechanizm, który wysyła tylko konkursy w których mc_ob jest równy obecnemu miesiącowo lub jeśli dzień jest pierwszym dniem miesiąca, to wysyłane są wyniki z poprzedniego miesiąca.