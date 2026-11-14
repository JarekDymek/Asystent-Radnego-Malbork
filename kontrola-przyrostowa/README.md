# Kontrola przyrostowa Asystenta Radnego — Malbork, IX kadencja

Oddzielne narzędzie **audytu przyrostowego**, a nie kopia publicznej wyszukiwarki PWA.

## Zakres i architektura

- Publiczna PWA: https://jarekdymek.github.io/Asystent-Radnego-Malbork/ — wersja **1.61.0**, manifest z 10.11.2026.
- Bazowy master: **v1.58** (1564 źródła, 243 pozycje braków, 14 zadań backfillu, 817 interpelacji i 677 odpowiedzi).
- Wersja 1.61.0: **709 odpowiedzi** dzięki 32 nowym pismom z 10.11 (30 przypisanych, 2 nadal bez jednoznacznego przypisania). Skan 55 stron nie ma pełnej transkrypcji.
- Panel zapisuje decyzje operatora lokalnie i generuje wyłącznie manifest-kandydata, **bez automatycznego wdrożenia**.

## Pliki tej gałęzi

- `index.html` — **wersja bez prywatnej korespondencji**; przeznaczona do osadzenia w osobnej stronie po sprawdzeniu dostępu.
- `samouczek.html` — animowana, interaktywna prezentacja działania (symulowane ekrany; bez wiadomości prywatnych).
- Prywatna wersja z zaimportowanym masterem i metadanymi korespondencji radnego dostarczana jest użytkownikowi **oddzielnie przez bezpieczny plik do pobrania**, nigdy przez publiczny GitHub.

## Funkcje

Deduplikacja po identyfikatorach, import XLSX/JSON/CSV/TSV, powiązania z publicznym PWA, kolejka backfillu, kontrola HTTP/CORS, pięć statusów, rejestr braków, porównanie wersji, historia przetwarzania, ręczne potwierdzanie dokumentów na podstawie dwóch źródeł i eksport manifestu po przejściu bramek.

## Integracja danych

Otwórz plik w aktualnej przeglądarce. W wariancie bez danych możesz zaimportować `seed-master.json` lokalnie jako **stan bazowy**, bez oznaczania rekordu jako nowego; w razie późniejszego importu ten sam identyfikator nie zostanie powielony. Migawki korespondencji JSON mogą być wczytywane tylko do kontrolowanego środowiska operatora.

## Bezpieczeństwo i ograniczenia

- W tej gałęzi **nie ma wiadomości Gmail, identyfikatorów kont ani niepublicznych załączników**.
- `localStorage` nie jest szyfrowany i nie zapewnia synchronizacji urządzeń. Nie udostępniaj prywatnego pliku HTML ani jego kopii.
- Bez własnego backendu, OAuth i kontroli dostępu nie ma automatycznego odczytu Gmail przez stronę; migawki są statyczne.
- BIP może blokować dostęp CORS. Tego nie należy interpretować jako HTTP 404.
- Nie wykonano automatycznej transkrypcji zeskanowanych 55 stron i nie wolno oznaczać ich jako w pełni odczytane.
- To **gałąź robocza**, nie opublikowana strona Sites. Osadzenie w Sites wymaga dostępnego hostingu i właściwych uprawnień.

## Ochrona publicznej aplikacji

`main/index.html`, `main/sw.js`, `main/version.json` i publiczne pakiety `data/` pozostają nienaruszone. Nie wolno scalać gałęzi lub aktualizować PWA automatycznie.