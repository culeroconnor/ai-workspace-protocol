---
name: knowledge-promotion
description: Identificar, normalizar, verificar y promover aprendizajes reutilizables o preferencias personales desde sesiones de IA, sin globalizar información de proyectos ni secretos.
---

# Knowledge promotion — Curaduría basada en evidencia

> Procedimiento reconstruido del informe. Ninguna base de IA Conociendome o Project_Brain_Generic se modifica al leerlo.

## Cuándo usar

Al cerrar una unidad lógica, detectar fallos repetidos, resolver un problema reproducible, observar una preferencia expresamente declarada o revisar candidatos de conocimiento.

## Pipeline

`RAW EVENT → CANDIDATE LESSON → normalizar + contrastar → REVIEWED LESSON → aprobación → destino`.

1. Identificar evento/decisión/errores/fix con **evidence_refs** accesibles.
2. Redactar candidato con `lesson_id`, `summary`, `problem`, `conditions`, `action_or_fix`, `evidence_refs`, `confidence`, `source_project_id`, `privacy`, `candidate_destination`, `review_status`.
3. Si es fallo, registrar explícitamente `lesson_type=failed_approach`, `attempt`, `why_it_failed`, `better_approach`, `do_not_apply_when`.
4. Normalizar error quitando rutas volátiles, números de línea, tokens y timestamps; vincular repetición entre sesiones con cautela.
5. Clasificar con separación estricta:
   - `user_profile`: preferencias explícitas del usuario o corroboradas consistentemente en múltiples sesiones. No inferir rasgos personales de una sola interacción.
   - `Project_Brain_Generic`: patrón técnico aplicable a más de un proyecto, verificado y acompañado de condiciones de uso, contraejemplos y evidencia.
   - `project_brain`: rutas, normas, dimensiones, decisiones, compromisos y pendientes del proyecto puntual.
6. Deduplicar y comprobar que la generalización no contradice otras evidencias; consignar `do_not_apply_when`.
7. Revisar clasificación, privacidad, alcance, evidencia y autorización del usuario/política real del destino.
8. Sólo después de aprobación y acceso verificado, escribir en el destino. Si no hay herramienta/permiso, entregar un candidato portable sin afirmar promoción.
9. Crear evento `learning_promoted` sólo si una lectura posterior confirma la escritura real; de lo contrario conservar `learning_candidate`.

## Criterios de rechazo / advertencia

- Un único comentario ambiguo NO es preferencia global estable.
- Un resultado reportado por otra IA sin prueba NO es fix validado.
- Un dato específico de ingeniería/arquitectura NO es regla transversal.
- Un secreto o dato privado NO se publica en brain genérico.
- Un patrón fallido puede documentarse como conocimiento negativo sin elevarlo a recomendación.

## Resultado

Resumen breve con `candidate_id`, destino, evidencia, condiciones de aplicación, excepción, decisión de revisión, estado real de escritura y, si quedó pendiente, acción humana siguiente.
