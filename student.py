from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class Gender(StrEnum):
    MALE = "Masculino"
    FEMALE = "Feminino"


class ASE(StrEnum):
    A = "A"
    B = "B"
    C = "C"


@dataclass
class Student:
    process_no: str
    name: str
    bdate: date
    age: int
    gender: Gender
    special_education_needs: bool = False
    naturality: str | None = None
    nationality: str | None = None
    address: str | None = None
    zip_code: str | None = None
    personal_email: str | None = None
    phone_number: str | None = None
    cellphone_number: str | None = None
    ase: ASE | None = None
    number_family_members: int | None = None
    foreign_language_I: str = "Inglês"
    foreign_language_II: str | None = None
    computer_at_home: bool = False
    internet_at_home: bool = False
    cc: str | None = None
    cc_archive: str | None = None
    cc_emission_date: date | None = None
    cc_validity_date: date | None = None
    passport: str | None = None
    NIF: str | None = None
    health_number: str | None = None
    NISS: str | None = None
    father_name: str | None = None
    father_naturality: str | None = None
    father_nationality: str | None = None
    father_contacts: str | None = None
    father_school: str | None = None
    father_job: str | None = None
    father_job_situation: str | None = None
    mother_name: str | None = None
    mother_naturality: str | None = None
    mother_nationality: str | None = None
    mother_contacts: str | None = None
    mother_school: str | None = None
    mother_job: str | None = None
    mother_job_situation: str | None = None
    guardian_relation: str | None = None
    guardian_name: str | None = None
    guardian_naturality: str | None = None
    guardian_nationality: str | None = None
    guardian_contacts: str | None = None
    guardian_email: str | None = None
    guardian_address: str | None = None
    guardian_zip_code: str | None = None
    guardian_school: str | None = None
    guardian_job: str | None = None
    guardian_job_situation: str | None = None
