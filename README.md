## Abbreviations:
C - create 
R - read
U - update
D - delete
CRU/R/CRUD - set of corresponding operations
assoc table - association table
LP - learning program
CL / level - language complexity level
kc - keycloak

- identified_created_updated - mixin to of common columns for some table
  - id: int
  - uuid: varchar
  - created_at: datetime
  - updated_at: datetime

- identified
  - id: int

## Business logic entities and description:

### Overall description:
App for foreign language learners to 
- read texts with easy translation of words and phrases
- listen to texts/words/phrases with voice
- learn used grammars identified by ai in texts (from created ones by admins)
- pass tests for repeating passed words/grammars (ai generated/flashcards by word/flashcards by images)
- to monitor progress of passed words/grammars

- ai (based on created by head complexity levels, created by admins word.level/grammar.level) via api (openai for example) will be able to 
  - identify complexity of some text
  - generate texts for particular level/words/grammars


### Registered user's roles and permissions:

- head
- admin
- premium
- guest
- anonymous (no role)

#### head 
- description: 
  - owner of service
  - have access to head panel app

- permissions:
  - CRUD 'user'
  - CRU 'language'
  - CRUD 'user_language' assoc (determine for admins in which langs admin is allowed to CRU 'word'/ 'grammar')
  - CRU 'level' (complexity level according to existing official language levels)
  - CRUD all entities created by admins
  - R all statistics etc

#### admin
- description:
  - employee who can edit complexity levels of words, create grammars
  - have access admin panel app

- permissions:
  - R 'language'
  - CRU 'word' assoc
  - CRU 'grammar' assoc
  - CRUD 'file' / 'word-file' assoc (word-image, word-audio) images are used in ai generated tests (image-flashcards)


#### premium / guest / anonymous
- description:
  - user of app
  - have access to user app

- functionality:
  - upload texts to his/her stash as files (txt, epub, pdf, docx, etc) or as raw text or as link to page with text
  - read texts uploaded (with 'tap to word' or 'select phrase' translations)
  - save words/phrases as 'to learn' / 'known'
  - generate and save mnemonic images to saved words/phrases (ai generated)
  - play words/phrases with voice (ai generated)
  - read texts provided by app (ai generated) based on user preferences:
    - theme
    - words / grammars marked by user as 'to learn' / 'known' (and words/grammars complexity level)
  - can see grammar structure explanations rules regarding particular word/phrase (ai generated)
  - monitor his/her progress (new 'known' words/grammars, its weight based on words/grammars complexity level)
  - generate tests for repeating 'to learn' words/grammars (ai generated)

- permissions:
  - 'anonymous' role user:
    - R 'readstash_text'
    - R 'word'
    - R 'word_image' (standard created by admin)
    - R 'grammar'
  - 'guest' role user:
    - all above
    - R 'user_progress' (new 'known' words/grammars, its weight based on words/grammars complexity level)
    - RUD 'user_word' (mark as 'known'/'to repeat')
  - 'premium' role user:
    - all above
    - CRUD 'word_image' (generate 'mnemonic' images for saved words)
    - RUD 'test' (generate 'tests' for repeating 'to learn' words/grammars)

## tables:

- language (identified_created_updated)
  - iso2: varchar (iso2 code like 'RU'/'EN'/'ES')
  - name: varchar (utf-8 string with native transcriptions like 'Русский'/'English'/'Español')

- level (identified_created_updated)
  - language_uuid: uuid
  - order: int (1, 2, 3, 4, 5, 6)
  - cefr_name: varchar ('A1' / 'A2' / 'B1' / 'B2' / 'C1' / 'C2') (for english - level of CEFR, for other languages - mapping CEFR levels of english translation)
  - native_name: varchar ('HSK-1', 'HSK-2', ... (in chinese) 'ТРКИ-1', 'ТРКИ-1+'... (in russian) 'A1', 'A2'... (in english)) (for english - the same as cefr_name, for others - mapping to native test level)

- word (identified_created_updated)
  - characters: varchar (utf-8 string with native transcriptions like 'слово'/'word'/'vocablo'/'單字')
  - language_uuid: uuid
  - level_uuid: uuid
  
  - image: relation (to file_index through word_file_user_status where file_index.content_type is image and user is NULL)
  - audio: relation (to file_index through word_file_user_status where file_index.content_type is audio and user is NULL)

- readstash_text (identified_created_updated)
  - content: text
  - level_uuid: uuid (determined by ai 'just as abstract' first, then can be modified by admin by info got by manually lunched process of calculation of used grammars and its average levels (determined and corresponded to existing grammars by ai), of used words and its average levels)
  - user_uuid: uuid

- phrase (identified_created_updated)
  - content: varchar (up to 500 chars for example)
  - level_uuid: uuid (-//-)
  - user_uuid: uuid

- grammar (identified_created_updated)
  - name: json ({'RU': 'имя', 'EN': 'name', 'ES': 'nombre'})
  - explanation: json ({'RU': 'объяснение', 'EN': 'explanation', 'ES': 'explicación'})
  - examples: json (['пример1', 'пример2']) (will be filled only in original language)
  - language_uuid: uuid (original language of grammar fk to russian, for example (will be filled to name first, then others langs will be filled by ai))
  - level_uuid: uuid

- file_index (identified_created_updated)
  - name: varchar
  - content_type: varchar
  - file_storage_uuid: uuid

- file_storage (identified_created_updated)
  - file_data: bytea

- word_file_user_status assoc
  - word_uuid: uuid
  - file_index_uuid: uuid | None
  - user_uuid: uuid | None
  - status: varchar

  a) admin uploaded image to word - row 1 created:
    - word_uuid: uuid, file_index_uuid: uuid1, user_uuid: NULL, status: NULL
  b) user saved word - row 1 copied, row 2 created, user changed status - row 2 changed:
    - word_uuid: uuid, file_index_uuid: NULL, user_uuid: uuid, status: 'to_learn'/ 'known'
  c) user generated image, row 2 changed:
    - word_uuid: uuid, file_index_uuid: uuid2, user_uuid: uuid, status: 'to_learn'/ 'known'

- user (identified_created_updated) some columns taken and to be synced with kc, some just here
  - uuid: uuid (from kc)
  - email: varchar (from kc)
  - first_name: varchar (from kc, full name)
  - last_name: varchar (from kc, always to NULL or '')
  - roles: json (roles from kc)
  - is_active: bool (from kc.is_enabled)
  - timezone: varchar
  - telegram_id: varchar
  - is_accepting_emails: bool
  - is_accepting_telegram: bool
  - is_accepting_interface_messages: bool
  - language_uuid: uuid (user's native language)

## Architecture entities:
- nginx (nginx) - reverse proxy, load balancer
- api_readstash (python, fastapi) - api with auth routes for registered head/admin/premium/guest, public routes for anonymous users
- keycloak:
  - keycloak(java, keycloak) - auth server
  - postgres_keycloak (postgres) - keycloak tables db
- postgres_readstash (postgres) - all tables db
- angular_readstash (typescript, angular) - web app interface for all users by routes:
  - readstash.com/head (for head)
  - readstash.com/admin (for admin)
  - readstash.com/ (for guest/premium/anonymous)
- redis_readstash (redis) - cache for api_readstash
- grafana/prometheus - (grafana, prometheus) monitoring

### Architectural requirements:
- scalable, new servers could be added to balance load
- robust and steady, 
- if some server goes down, users must have access not to 'write' operations but at least to 'read' from the closest available postgres_readstash replica


# Usage:

- create text:

```

```