from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password
import os


pf = PetFriends()

""" Проверяем, что при запросе API ключа возвращается статус-кода 200 и 'key' содержится в result:"""
def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert 'key' in result

""" Проверяем, что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем API ключ и сохраняем в переменную auth_key. Далее используя этот ключ
    запрашиваем список всех питомцев и проверяем, что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """
def test_get_all_pets_with_valid_key(filter=''):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0

"""Проверяем возможность создания питомца без фотографии"""
def test_successful_pet_without_photo_created(name='Евгениус', animal_type='dog', age='3'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.create_a_pet_without_photo(auth_key, name, animal_type, age)
    assert status == 200
    assert result['name'] == name

"""Проверяем невозможность создания питомца, в случае незаполнения обязательных параметров: name, animal_type, age"""
def test_cannot_add_a_pet_with_blanc_name_type_age(name='', animal_type='', age=''):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.create_a_pet_without_photo(auth_key, name, animal_type, age)
    assert status == 400 #баг платформы, создает питомца и возвращает код 200

"""Проверяем невозможность создания питомца, в случае заполнения параметра age отрицательным числом"""
def test_cannot_add_a_pet_with_invalid_age(name='Малыш', animal_type='cat', age='-2'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.create_a_pet_without_photo(auth_key, name, animal_type, age)
    assert status == 400 #баг платформы, создает питомца с отрицательным возрастом и возвращает код 200

"""Проверяем невозможность создания питомца, в случае заполнения параметра age символами"""
def test_cannot_add_a_pet_with_invalid_age2(name='Хома', animal_type='homyak', age='@#/*'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.create_a_pet_without_photo(auth_key, name, animal_type, age)
    assert status == 400 #баг платформы, создает питомца с символами вместо возраста и возвращает код 200

""" Проверяем невозможность создания питомца в случае заполнения параметра age очень большим числом"""
def test_post_add_pet_no_valid_age_max(name='Лейла', animal_type='horse', age='1000'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.create_a_pet_without_photo(auth_key, name, animal_type, age)
    assert status == 400 #баг платформы, создает питомца с очень большим возрастом и возвращает код 200

"""Проверяем на наличие ранее добавленных питомцев пользователем"""
def test_my_pets_have_any_pet(filter='my_pets'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter='my_pets')
    assert status == 200
    assert len(result['pets']) > 0

"""Проверяем возможность добавления или обновления фотографии существующего питомца"""
def test_add_photo_to_existing_pet_successfully(pet_photo='images/456.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_id = my_pets['pets'][0]['id']
    status, result = pf.add_photo_to_existing_pet(auth_key, pet_id, pet_photo)
    assert status == 200
    assert len(result['pet_photo']) > 0

"""Проверяем возможность удаления карточки питомца"""
def test_successful_delete_self_pet():
    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    # Проверяем - если список своих питомцев пустой, то добавляем нового, повторно запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Буся", "cat", "1", "images/789.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)
    # Повторно запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    # Проверяем, что статус-код 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()

"""Проверяем на невозможность добавления текстового файла вместо фотографии существующего питомца"""
def test_cannot_add_text_file_as_existing_pet_photo(pet_photo='images/11111.txt'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_id = my_pets['pets'][0]['id']
    status, result = pf.add_photo_to_existing_pet(auth_key, pet_id, pet_photo)
    assert status == 400

"""Проверяем получение API ключа для невалидного email"""
def test_cannot_get_api_key_invalid_email(email=invalid_email, password=valid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result

"""Проверяем получение API ключа для невалидного password"""
def test_cannot_get_api_key_invalid_password(email=invalid_email, password=invalid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result

"""Проверяем на ввод невалидного email и невалидого password и на наличие 'key' в result"""
def test_api_key_with_incorrect_password_invalid_email(email = invalid_email, password = invalid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result





