public static void sanitizeDocument(final PDFDocument document, final URL sanitizedUrl)
                    throws PDFInvalidDocumentException, PDFIOException, PDFSecurityException, PDFFontException,
                    PDFConfigurationException, PDFInvalidParameterException, PDFUnableToCompleteOperationException {
        if (!canSanitizeDocument(document)) {
            LOGGER.warn("The document was not sanitized");
            return;
        }
        ByteWriter writer = null;
        try {
            writer = IoUtils.newByteWriter(sanitizedUrl);
        } catch (final IOException e) {
            throw new PDFIOException(e);
        }
        final PDFSaveOptions saveOptions = PDFSaveLinearOptions.newInstance();
        saveOptions.setForceCompress(true);
        final SanitizationOptions options = new SanitizationOptions();
        Runnable _extracted_0 = () -> {
        options.setPDFFontSet(FontSetLoader.newInstance().getFontSet());
        options.setSaveOptions(saveOptions);
        SanitizationService.sanitizeDocument(document, options, writer);
        };
        _extracted_0.run();
    }