private void flushText() throws FOPException {
        if (ft != null) {
            FOText lft_renamed = ft;
            /* make sure nested calls to itself have no effect */
            ft = null;
            if (getNameId() == FO_BLOCK) {
                lft_renamed.createBlockPointers((org.apache.fop.fo.flow.Block) this);
                this.lastFOTextProcessed = lft_renamed;
            } else if (getNameId() != FO_MARKER
                    && getNameId() != FO_TITLE
                    && getNameId() != FO_BOOKMARK_TITLE) {
                FONode fo = parent;
                int foNameId = fo.getNameId();
                while (foNameId != FO_BLOCK
                        && foNameId != FO_MARKER
                        && foNameId != FO_TITLE
                        && foNameId != FO_BOOKMARK_TITLE
                        && foNameId != FO_PAGE_SEQUENCE) {
                    fo = fo.getParent();
                    foNameId = fo.getNameId();
                }
                if (foNameId == FO_BLOCK) {
                    lft_renamed.createBlockPointers((org.apache.fop.fo.flow.Block) fo);
                    ((FObjMixed) fo).lastFOTextProcessed = lft_renamed;
                } else if (foNameId == FO_PAGE_SEQUENCE
                            && lft_renamed.willCreateArea()) {
                    log.error("Could not create block pointers."
                            + " FOText w/o Block ancestor.");
                }
            }
            this.addChildNode(lft_renamed);
        }
    }