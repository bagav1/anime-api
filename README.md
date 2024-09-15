# AnimeAPI

## Description
This project is a combination of two modules: **[animeflv](https://animeflv.net)** and **[jkanime](https://jkanime.net)**, which serve to obtain anime information and links from the respective platforms. It uses **web scraping** to collect data, allowing developers to access a wide range of anime and episode information.

## Project Structure
- **animeflv/**: Contains the functions related to AnimeFLV scraping.
  - `animeflv.py`: Main class to handle interaction with AnimeFLV, including getting anime and episode information.
  - `schema.py`: Define data schemas using Pydantic to validate and structure the data obtained.
- **jkanime/**: Similar to `animeflv`, but designed for the JKAnime platform.
  - `jkanime.py`: Main class that handles scraping and obtaining data from JKAnime.
  - `schema.py`: Defines the data schemas specific to the JKAnime data structure.
- **requirements.txt**: List of dependencies required to execute the project.

## Dependencies
The project requires the following libraries:
- `cloudscraper` (1.2.71)
- `lxml` (5.3.0)
- `beautifulsoup4` (4.12.3)
- `pydantic` (2.8.2)

Para instalar las dependencias, utiliza el siguiente comando:
```bash
pip install -r requirements.txt
```

## Functionality
### AnimeFLV
- `AnimeFLV`: Class to interact with the AnimeFLV site, getting links to episodes and anime listings.
  - Featured methods:
    - `get_links(id, episode)`: Get the download links for a specific episode.
    - `get_latest_episodes()`: Returns a list of recently released episodes.

### JKAnime
- `JKAnime`: Clase para manejar la interacción con JKAnime, permitiendo buscar animes y obtener información detallada.
  - Featured methods:
    - `list(page)`: Retrieves a list of anime in the JKAnime directory.
    - `get_anime_info(id)`: Get detailed information about a specific anime.

## How to Use
To use the project classes, import the corresponding module and create an instance of the desired class.

### Example of Use:
```python
from jkanime import JKAnime
from animeflv import AnimeFLV

# Example with JKAnime
with JKAnime() as api:
    anime_info = api.get_anime_info("tensei-shitara-slime-datta-ken-3rd-season")
    print(anime_info)

# Example with AnimeFLV
with AnimeFLV() as api:
    anime_info = api.get_anime_info("nanatsu-no-taizai")
    print(anime_info)
```

## Note
This project scrapes from animeflv.net and jkanime.net platforms. Be sure to comply with the terms of service of the platforms before using this project.
> Indirect fork of [jorgeajimenezl/animeflv-api](https://github.com/jorgeajimenezl/animeflv-api).
> Use and improvement of the animeflv module, since the original one seems not to be currently supported (New PR's).

## Contributions
Contributions are welcome. If you wish to contribute, please create a fork of the repository and send a pull request with your changes.

## Licencia
This project is licensed under the [MIT](./LICENSE) License. For more information, see the LICENSE file.