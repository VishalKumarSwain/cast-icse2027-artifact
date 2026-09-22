import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_7485b60696ad_t {
public eu.hyvar.feature.expression.resource.hyexpression.ui.HyexpressionCompletionProposal[] computeCompletionProposals(eu.hyvar.feature.expression.resource.hyexpression.IHyexpressionTextResource originalResource, String content, int cursorOffset) {
		ResourceSet resourceSet_renamed = new ResourceSetImpl();
		eu.hyvar.feature.expression.resource.hyexpression.IHyexpressionTextResource resource = (eu.hyvar.feature.expression.resource.hyexpression.IHyexpressionTextResource) resourceSet_renamed.createResource(originalResource.getURI());
		ByteArrayInputStream inputStream = new ByteArrayInputStream(content.getBytes());
		eu.hyvar.feature.expression.resource.hyexpression.IHyexpressionMetaInformation metaInformation = resource.getMetaInformation();
		eu.hyvar.feature.expression.resource.hyexpression.IHyexpressionTextParser parser = metaInformation.createParser(inputStream, null);
		eu.hyvar.feature.expression.resource.hyexpression.mopp.HyexpressionExpectedTerminal[] expectedElements = parseToExpectedElements(parser, resource, cursorOffset);
		if (expectedElements == null) {
			return new eu.hyvar.feature.expression.resource.hyexpression.ui.HyexpressionCompletionProposal[0];
		}
		if (expectedElements.length == 0) {
			return new eu.hyvar.feature.expression.resource.hyexpression.ui.HyexpressionCompletionProposal[0];
		}
		List<eu.hyvar.feature.expression.resource.hyexpression.mopp.HyexpressionExpectedTerminal> expectedAfterCursor = Arrays.asList(getElementsExpectedAt(expectedElements, cursorOffset));
		List<eu.hyvar.feature.expression.resource.hyexpression.mopp.HyexpressionExpectedTerminal> expectedBeforeCursor = Arrays.asList(getElementsExpectedAt(expectedElements, cursorOffset - 1));
		setPrefixes(expectedAfterCursor, content, cursorOffset);
		setPrefixes(expectedBeforeCursor, content, cursorOffset);
		Collection<eu.hyvar.feature.expression.resource.hyexpression.ui.HyexpressionCompletionProposal> allProposals = new LinkedHashSet<eu.hyvar.feature.expression.resource.hyexpression.ui.HyexpressionCompletionProposal>();
		Collection<eu.hyvar.feature.expression.resource.hyexpression.ui.HyexpressionCompletionProposal> rightProposals = deriveProposals(expectedAfterCursor, content, resource, cursorOffset);
		Collection<eu.hyvar.feature.expression.resource.hyexpression.ui.HyexpressionCompletionProposal> leftProposals = deriveProposals(expectedBeforeCursor, content, resource, cursorOffset - 1);
		removeKeywordsEndingBeforeIndex(leftProposals, cursorOffset);
		allProposals.addAll(leftProposals);
		int leftMatchingProposals = 0;
		for (eu.hyvar.feature.expression.resource.hyexpression.ui.HyexpressionCompletionProposal leftProposal : leftProposals) {
			if (leftProposal.isMatchesPrefix()) {
				leftMatchingProposals++;
			}
		}
		if (leftMatchingProposals == 0) {
			allProposals.addAll(rightProposals);
		}
		final List<eu.hyvar.feature.expression.resource.hyexpression.ui.HyexpressionCompletionProposal> sortedProposals = new ArrayList<eu.hyvar.feature.expression.resource.hyexpression.ui.HyexpressionCompletionProposal>(allProposals);
		Collections.sort(sortedProposals);
		EObject root = null;
		if (!resource.getContents().isEmpty()) {
			root = resource.getContents().get(0);
		}
		for (eu.hyvar.feature.expression.resource.hyexpression.ui.HyexpressionCompletionProposal proposal : sortedProposals) {
			proposal.setRoot(root);
		}
		return sortedProposals.toArray(new eu.hyvar.feature.expression.resource.hyexpression.ui.HyexpressionCompletionProposal[sortedProposals.size()]);
	}
}
