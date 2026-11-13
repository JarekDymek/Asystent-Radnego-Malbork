# Kontrola przyrostowa Asystenta Radnego — IX kadencja Rady Miasta Malborka

Odrębny, responsywny panel administracyjny. **Nie jest zamiennikiem publicznej PWA.** Nie zmienia plików w repozytorium `main`, w szczególności `sw.js` i `version.json`. Nie publikuje zmian automatycznie.

## Uruchomienie

Otwórz `index.html` w aktualnej wersji Chrome/Edge/Safari lub opublikuj go na **odrębnym**, kontrolowanym dostępowo hostingu statycznym, a następnie osadź URL w Sites. W przeglądarce zaimportuj master XLSX z własnego dysku. Samo otwarcie strony nie powoduje importu ani przesłania bazy.

Panel jest niezależny od istniejącej [publicznej aplikacji](https://jarekdymek.github.io/Asystent-Radnego-Malbork/). Odczytuje wyłącznie jej publiczny numer wersji z `version.json`. Biblioteczny master `Asystent_Radnego_Master_IX_kadencja_v1.58.xlsx` i publiczny pakiet `1.61.0` nie są utożsamiane.

## Funkcje

- Import XLSX/CSV/TSV/JSON; deduplikacja po identyfikatorach, URL i opcjonalnym SHA; historia partii.
- Rejestr BIP, pięć statusów, kontrola adresów i obsługa błędów HTTP/CORS.
- Kolejka backfillu, braki, porównanie do punktu kontrolnego.
- Status „zweryfikowane” po potwierdzeniu oficjalnego źródła, treści, identyfikacji, niezależnego źródła i kontrolującego.
- Blokada ponownego przetwarzania sprawdzonych rekordów oraz otwarcie kontroli po wykryciu zmiany.
- Eksport *manifestu-kandydata* do publikacji dopiero po przejściu bramek jakości, bez commitu i wdrożenia.

## Granice i bezpieczeństwo

Dane robocze znajdują się tylko w `localStorage` danej przeglądarki. Nie ma wielostanowiskowej synchronizacji ani centralnej autoryzacji. **Regularnie eksportuj kopię JSON.** Dostęp do hostowanego panelu powinien być ograniczony po stronie hostingu.

Przeglądarka może blokować odczyt BIP przez CORS, co **nie dowodzi** nieistnienia dokumentu. Panel nie wykonuje OCR skanów ani kompletnego crawlera BIP. Master importowany jest lokalnie, nie należy umieszczać poufnych danych w publicznym GitHubie.

Kod panelu znajduje się tylko w gałęzi `sites-kontrola-przyrostowa-20261113` w katalogu `kontrola-przyrostowa/`. Gałąź `main` pozostaje bez zmian.
