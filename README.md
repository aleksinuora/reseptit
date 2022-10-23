# Reseptikirja

Palvelu joka ehdottaa käyttäjän tallentamia reseptejä älykkäästi.
Suositukseen vaikuttavia painoja voivat olla esim. reseptin suosio,
kulunut aika sen viimeisestä käytöstä, sesonki jne. Projektia voi
tarpeen mukaan laajentaa ravintoarvoilla, ehdottamalla käyttökohteita
tähteille ja muille kaapissa oleville ruoka-aineille tai lisäämällä
resepteihin kommentointimahdollisuuden.

## Käyttö

Palvelua voi testata osoitteessa:
https://ruokaideat.herokuapp.com/

Tietokannassa on valmiina testitili jolla voi kokeilla
kirjautumista ja sitä vaativia ominaisuuksia:
Käyttäjänimi='Testaaja'
Salasana='salasana'

### Sovelluksen tila, loppupalautus

Palvelu näyttää etusivulla satunnaisen reseptiehdotuksen.
Reseptejä voi selata vapaasti ja hakea lisääjän/raaka-aineiden
perusteella.

Käyttäjätilin luomisen ja kirjautumisen jälkeen käyttäjä voi
myös lisätä, poistaa ja muokata omia reseptejään ja kommenttejaan.
Käyttäjän omat reseptit ja kommentit näkyvät erillisellä profiilisivulla.

Palvelussa on valmiiksi vapaasti käytettävä tili 'Testaaja' salasanalla
'salasana' joka toimii lähes täysin samalla tavalla kuin tavalliset
tilit. 'Testaaja' ei kuitenkaan voi poistaa omaa tiliään lopullisesti.

### Sovelluksen tila, välipalautus 3

Toteutetut ominaisuudet:
* Uuden tilin luominen
* Kirjautuminen
* Käyttäjän profiilisivu
* Käyttäjän poistaminen
* Satunnaisen reseptin näyttäminen etusivulla
* Reseptien lisäys
* Reseptien listaus
* Reseptihaku nimen, raaka-aineiden ja/tai 
    lähettäjän perusteella
* Reseptin poisto
* Reseptien kommentointi
* Kommenttien poisto ja muokkaus
* Käyttöoikeuksien valvonta ja admin-tili
* Alustava ulkoasu Bootstrapilla

### Sovelluksen tila, välipalautus 2

Sovelluksella on alkeellinen toimiva pohja. Tietokannasta voi hakea
reseptejä id:n perusteella.
