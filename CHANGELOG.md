# Asystent Radnego — zmiany

## 1.64.1 (2026-11-24)

- Archiwum w zakładce Analiza uchwał: 255 aktów z 35 sesji, istniejące ustalenia audytu i relacje, jawne oznaczenia braków.
- Odczyt i weryfikacja pakietu katalogowego również przy bezpośrednim otwarciu modułu.
- Zachowano wersję danych 1.63.0.

## 1.64.0 (2026-11-24)

- Zakładka Analiza uchwał, publiczny porządek XXXVII sesji, lokalny import raportów, historia wersji, pytania i notatki.
- Porównanie z dotychczasowym indeksem uchwał, audytem oraz zaimportowanymi pełnymi tekstami.
- Buforowanie modułu offline; dane katalogowe pozostają w wersji 1.63.0.

## 1.63.0 (2026-11-23)

- Publiczna projekcja zweryfikowanych rekordów centralnego mastera v1.63 (stan na 22.11.2026).
- Sześć przyjętych uchwał XXXVI/297–302/2026; liczba uchwał w PWA 249 → 255.
- Jeden publiczny zapis informacji medialnej o ustnej wypowiedzi dotyczącej ul. Targowej, **nie jest to formalna pisemna odpowiedź**; liczba rekordów odpowiedzi 709 → 710.
- Liczniki bez zmian: 817 interpelacji i zapytań, 336 głosowań, 6207 głosów imiennych, 251 aktów audytu.
- Zachowano 32 wcześniej zaimportowane pisma listopadowe i ich 32 logiczne relacje. Bez powtórnego importu.
- Wyłączono skany, treści wiadomości, identyfikatory i adresy Gmail, niezweryfikowane prywatne projekty oraz historyczne braki; migracja kanoniczna pozostaje nieukończona.
- Zmieniono manifest, cache PWA i panel nowości. Spójność gzip, SHA-256 i SQLite sprawdzona przed wdrożeniem.

## 1.61.0 (2026-11-10)

- Zapisano **32 pisma** z pakietu odpowiedzi Biura Rady (55 stron PDF, oryginały w Bibliotece prywatnej).
- **30 pism** powiązano z interpelacjami sesji XXXVI; **32 relacje** (jedno pismo obejmuje trzy pytania).
- **2 pisma** pozostały w kolejce do ustalenia numeru sprawy.
- Uzupełniono bazę operacyjną: 709 powiązanych rekordów odpowiedzi łącznie (677 wcześniej + 32 powiązania).
- W aplikacji dodano widoczne powiadomienie „Nowe dane” i wykaz zmian.
- **Ograniczenie:** skany nie zawierają warstwy tekstowej; poza jawnie sprawdzonymi fragmentami nie deklaruje się pełnych transkrypcji.
- Nie publikowano plików z Gmaila ani korespondencji prywatnej.

## 1.60.1 (2026-10-31)

- Sortowanie po dacie i lokalne zadawanie pytań do audytu uchwał.
