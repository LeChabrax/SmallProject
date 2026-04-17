# Mission Avis — Blast ambassadeurs ayant reçu leurs produits
**Date** : 17/04/2026
**Scope** : 137 ambassadeurs avec statut `Produits envoyés` dans `Suivi_Amb`
**Canaux** : Instagram DM (vidéo + texte) + Email (texte seul, Outlook copier-coller)

---

## Vidéo à envoyer (Instagram)
`tools/ContentInflu/AvisVideo-17-04-26/TutoAvisEspacePerso.mp4` (6.1 Mb)

---

## Draft message Instagram DM (tutoiement — règle ambassadeur)

> ⚠️ L'envoi vidéo via DM n'est plus supporté par l'API. On envoie un **message texte unique** avec un lien Drive vers la vidéo tuto.
> Sur Instagram on garde **toujours le prénom** dans le Hello (extraction depuis `full_name` Instagram, fallback "Hello !" si on ne le trouve pas).

```
Hello {prenom} ! J'espère que tu vas bien.

Super nouvelle, on est trop content de te présenter notre nouveauté : tu peux maintenant laisser un avis directement depuis ton espace perso sur notre site !

On t'a préparé une petite vidéo tuto pour t'expliquer, y'a plus qu'à suivre les instructions 😉
👉 https://drive.google.com/file/d/16NjXmEff9zZ-KDOSYmrNkApfmtXoLngU/view?usp=sharing

N'hésite pas à y faire un tour pour découvrir la nouvelle interface et déposer tes avis sur les produits que tu as reçus. Ça nous aide énormément 🙏

Sportivement,
Antoine
```

---

## Draft email (vouvoiement — client Shopify a acheté/reçu via compte impulse-nutrition.fr)

**Objet** : Nouveau : laissez vos avis directement depuis votre espace personnel

```
Bonjour,

Petite nouveauté à vous partager : vous pouvez désormais laisser un avis sur les produits Impulse Nutrition directement depuis votre espace personnel sur impulse-nutrition.fr.

N'hésitez pas à vous connecter pour découvrir la nouvelle interface et partager votre retour sur les produits que vous avez reçus. Vos avis nous aident énormément à faire évoluer la marque.

Merci pour votre soutien,

L'équipe Impulse Nutrition
```

> Note persona : ambassadeurs = tutoiement sur Instagram (canal humain, Antoine), mais en email mailing général = vouvoiement entité Impulse (plus cohérent avec l'expérience client mail Shopify qu'ils reçoivent). Si tu préfères tutoiement email aussi, dis-le.

---

## Plan d'exécution Instagram (à lancer quand tu donnes le go)

1. Pull liste `handles_instagram.md` (137 handles)
2. Pour chaque handle : `get_user_id_from_username` -> `send_video_message(video, caption)`
3. Délai random 30-60s entre chaque envoi (~1h40 pour les 137)
4. Queue JSON local pour reprise si coupure + éviter doublons
5. Log final envoyés / échecs / sans compte trouvé

**Bloquant avant lancement** :
- Choix prénom (1. extraction full_name Instagram / 2. sans prénom générique / 3. colonne prénom manuelle)
- Go par batch (10 test puis pause) ou go full
