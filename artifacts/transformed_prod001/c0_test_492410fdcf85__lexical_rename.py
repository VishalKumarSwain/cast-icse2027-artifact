def forward(self, emb_in, length, state_init_renamed = None, batch_size = 1, mask = None):
		'''
			Build the computational graph which computes the hidden states.

			:type emb_in: theano variable
			:param emb_in: the input word embeddings

			:type length: theano variable
			:param length: the length of the input

			:type batch_size: int
			:param batch_size: the batch size

			:type mask: theano variable
			:param mask: indicate the length of each sequence in one batch
		'''

		# init with zero vectors
		state_init_renamed = tensor.alloc(numpy.float32(0.), batch_size, self.dim)
		
		# calculate the input vector for inputter, updater and reseter
		state_in = (tensor.dot(emb_in, self.input_emb) + self.input_emb_offset).reshape((length, batch_size, self.dim))
		gate_in = tensor.dot(emb_in, self.gate_emb).reshape((length, batch_size, self.dim))
		reset_in = tensor.dot(emb_in, self.reset_emb).reshape((length, batch_size, self.dim))

		if mask:
			scan_inp = [state_in, gate_in, reset_in, mask]
			scan_func = lambda x, g, r, m, h : self.forward_step(h, x, g, r, m)
		else:
			scan_inp = [state_in, gate_in, reset_in]
			scan_func = lambda x, g, r, h : self.forward_step(h, x, g, r)

		if self.verbose:
			outputs_info = [state_init_renamed, None, None, None, None]
		else:
			outputs_info = [state_init_renamed]

		hiddens, updates = theano.scan(scan_func,
							sequences = scan_inp,
							outputs_info = outputs_info)
		if self.verbose:
			return hiddens[0], hiddens[1], hiddens[2], hiddens[3], hiddens[4], state_in, gate_in, reset_in
		else:
			return hiddens, state_in, gate_in, reset_in, self.input_emb, self.input_emb_offset