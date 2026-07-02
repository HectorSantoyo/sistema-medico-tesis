# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Sistema Médico — a Django MVP for a master's thesis (Maestría en Ciencias Computacionales, advisor Dr. Jesús García Camarena). Manages patients, appointments, and structured clinical history, with a rule-based engine that flags possible chronic-disease risk (diabetes, hipertensión, anemia) from symptom matches. All data is synthetic. Broader thesis context (chapters, references, disease list, academic decisions) lives in `../CLAUDE.md` one directory up — read it too when the task touches thesis framing or scope decisions, not just code.

**Note on stack drift:** the parent CLAUDE.md describes the target stack as Django 4.2 + MySQL. The repo as it stands runs **Django 5.2** and **SQLite** (`db.sqlite3`, see `sistemamedico/settings.py`). Don't "fix" this back to Django 4.2/MySQL unless the user asks — treat SQLite/5.2 as the current source of truth for how to run things.

## Commands

```bash
source env/bin/activate                 # env/ is the local virtualenv (already created, gitignored)
python3 -m pip install -r requirements.txt

python manage.py runserver
python manage.py migrate
python manage.py makemigrations <app>   # e.g. makemigrations historial_clinico
python manage.py createsuperuser

python manage.py test                   # all apps
python manage.py test historial_clinico # single app
python manage.py test pacientes.tests.SomeTestClass.test_method  # single test, once tests exist
```

There is no linter/formatter config, no Dockerfile, and no CI pipeline in the repo yet — these are still on the "falta por implementar" list in the parent CLAUDE.md.

## Architecture

Standard Django MTV, one app per domain concept, wired together in `sistemamedico/urls.py`:

```
usuarios/          Medico model (OneToOne -> auth.User), login/dashboard, doctor self-registration
pacientes/          Paciente model, always owned by a Medico via medico_asignado
citas/               Cita model, appointment CRUD (Agendada/Cancelada/Reprogramada/Finalizada)
historial_clinico/  RegistroClinico, Sintoma, Enfermedad models — views.py and forms.py are EMPTY, not yet built
analisis/            AlertaClinica model, read-only "active alerts" view; no detection logic yet
```

**Ownership chain:** `Medico` -> `Paciente.medico_asignado` -> `Cita`/`RegistroClinico`/`AlertaClinica` all FK to both `Paciente` and `Medico`. Every view fetches `Medico.objects.get(user=request.user)` first, then filters querysets by that medico — there is no cross-doctor access. Any new view must follow this same `@login_required` + `medico = Medico.objects.get(user=request.user)` + filter pattern (see `pacientes/views.py`, `citas/views.py`, `analisis/views.py` for the existing convention).

**Structured clinical model (Sprint 1, done):** `Sintoma` (`nombre` unique, `descripcion`) and `Enfermedad` (`nombre` unique, `descripcion`, `sintomas` ManyToMany -> `Sintoma`, `related_name="enfermedades"`) both exist in `historial_clinico/models.py`. `RegistroClinico` now has a `sintomas` ManyToMany -> `Sintoma` (`blank=True`, `related_name="registros_clinicos"`) in addition to its original fields. `diagnostico`, `tratamiento`, and `notas_adicionales` are kept as-is — free-text fields that complement the structured `sintomas`, not replaced by them.

**Current data model gap:** the structured model above exists, but there is no detection engine yet — no `post_save` signal, no `save()` override, and no logic anywhere that reads a `RegistroClinico`'s `sintomas`, compares them against `Enfermedad.sintomas`, computes a match-percentage, or creates `AlertaClinica` rows automatically. `analisis/views.py` still only reads existing `AlertaClinica` rows, it never creates them.

**URL structure:** each app owns its own `urls.py`, included from `sistemamedico/urls.py` with a prefix (`usuarios/`, `citas/`, `alertas/` for `analisis`; `pacientes` is mounted at the root `''`). `historial_clinico` has no `urls.py` yet since its views don't exist.

**Templates:** project-wide templates in top-level `templates/` (`base.html`, `login.html`, `registration/`); each app additionally has its own `templates/<app>/` for app-specific pages, following Django's `APP_DIRS` convention. `django-widget-tweaks` is installed for form rendering in templates.

**Forms:** `ModelForm` per app (`pacientes/forms.py`, `citas/forms.py`, `usuarios/forms.py`). Two established patterns to reuse: `CitaForm.__init__` accepts a `medico` kwarg to scope the `paciente` queryset to that doctor's patients; `PacienteForm` excludes `medico_asignado` and sets it in the view instead of the form.

## Conventions (from parent CLAUDE.md, enforced in this codebase)

- Model names: PascalCase in Spanish (`RegistroClinico`, `AlertaClinica`, `Paciente`).
- Variable/function names: snake_case in Spanish (`nivel_riesgo`, `fecha_generada`).
- Every data-access view: `@login_required` + filter by `medico = request.user.medico` (in practice, current code does `Medico.objects.get(user=request.user)` — either form is fine, keep the ownership filter itself intact).
