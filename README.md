# i18nMessagesPropertiesConverter
This is a simple app to make the process of creating messages.properties for pl/en easier

## Functionality
defaultly you can paste in your properties to translate
![defaultmode](https://github.com/user-attachments/assets/ca420c86-049b-4128-8187-c027478df997)
but there's mode to use file from chosen directory
![othermode](https://github.com/user-attachments/assets/7131d1b2-a191-473f-b457-20bd8fe94cdb)

## Usage
paste method
![usage](https://github.com/user-attachments/assets/8592d592-4f98-48a3-8a8a-61d2069708e6)
![usage2](https://github.com/user-attachments/assets/9dcc3ecf-ff11-40d8-b6e8-693ca760daad)
file method
![usage3](https://github.com/user-attachments/assets/a778ca2e-b4a2-41f3-b400-4241e92b0318)
![usage4](https://github.com/user-attachments/assets/5584a521-73b0-4044-bf09-44dc399929fc)


### contents of both created output files is:
example.module.section.ui.View.description=Sample description<br />
example.module.section.ui.View.title=Sample title<br />
example.module.section.ui.View.username=Username<br />
example.module.section.ui.View.password=Password<br />
example.module.section.ui.View.loginButton=Log in<br />

## Custom Dictionary
The app incorporates a custom dictionaries to facilitate localization and provide translations for specific terms. This dictionaries are divided into two JSON files: 'custom_dict_en.json', which stores translations from Polish to English, and 'custom_dict_pl.json', which stores translations from English to Polish. Each file follows a simple key-value format, where the key represents the term in the source language, and the corresponding value is its translation in the target language.
