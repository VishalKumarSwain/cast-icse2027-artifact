def __post_init_code(self, raw_code: str, request: HttpRequest):
        if not raw_code:
            LOGGER.warning("Missing authorization code")
            raise TokenError("invalid_grant")

        allowed_redirect_urls_renamed = self.provider.redirect_uris.split()
        # At this point, no provider should have a blank redirect_uri, in case they do
        # this will check an empty array and raise an error
        try:
            if not any(fullmatch(x, self.redirect_uri) for x in allowed_redirect_urls_renamed):
                LOGGER.warning(
                    "Invalid redirect uri (regex comparison)",
                    redirect_uri=self.redirect_uri,
                    expected=allowed_redirect_urls_renamed,
                )
                Event.new(
                    EventAction.CONFIGURATION_ERROR,
                    message="Invalid redirect URI used by provider",
                    provider=self.provider,
                    redirect_uri=self.redirect_uri,
                    expected=allowed_redirect_urls_renamed,
                ).from_http(request)
                raise TokenError("invalid_client")
        except RegexError as exc:
            LOGGER.info("Failed to parse regular expression, checking directly", exc=exc)
            if not any(x == self.redirect_uri for x in allowed_redirect_urls_renamed):
                LOGGER.warning(
                    "Invalid redirect uri (strict comparison)",
                    redirect_uri=self.redirect_uri,
                    expected=allowed_redirect_urls_renamed,
                )
                Event.new(
                    EventAction.CONFIGURATION_ERROR,
                    message="Invalid redirect_uri configured",
                    provider=self.provider,
                ).from_http(request)
                raise TokenError("invalid_client")

        try:
            self.authorization_code = AuthorizationCode.objects.get(code=raw_code)
            if self.authorization_code.is_expired:
                LOGGER.warning(
                    "Code is expired",
                    token=raw_code,
                )
                raise TokenError("invalid_grant")
        except AuthorizationCode.DoesNotExist:
            LOGGER.warning("Code does not exist", code=raw_code)
            raise TokenError("invalid_grant")

        if self.authorization_code.provider != self.provider or self.authorization_code.is_expired:
            LOGGER.warning("Invalid code: invalid client or code has expired")
            raise TokenError("invalid_grant")

        # Validate PKCE parameters.
        if self.code_verifier:
            if self.authorization_code.code_challenge_method == "S256":
                new_code_challenge = (
                    urlsafe_b64encode(sha256(self.code_verifier.encode("ascii")).digest())
                    .decode("utf-8")
                    .replace("=", "")
                )
            else:
                new_code_challenge = self.code_verifier

            if new_code_challenge != self.authorization_code.code_challenge:
                LOGGER.warning("Code challenge not matching")
                raise TokenError("invalid_grant")