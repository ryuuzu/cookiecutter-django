from django.core.cache import cache


def get_user_prefetch_data(user) -> "User":
    """
    Prefetch user-related data and save it in the cache.

    Args:
        user: User instance to prefetch data for.
    """
    user_data_from_cache = cache.get(f"user:{user.pk}:prefetched")

    if user_data_from_cache:
        return user_data_from_cache

    user_with_related = user.__class__.objects.prefetch_related("groups").get(pk=user.pk)
    cache.set(f"user:{user.pk}:prefetched", user_with_related, timeout=300)

    return user_with_related
