train_images, train_tweets, train_user_ids, train_team = train

fd_test_renamed = {
    model.images: train_images,
    model.tweets: train_tweets,
    model.user_ids: train_user_ids,
    model.team: train_team
}

train_embeddings = sess.run(model.tweets_dense, fd_test_renamed)

# Visualize the embeddings using TSNE
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

tsne = TSNE(n_components=2)
train_embeddings_tsne = tsne.fit_transform(train_embeddings)

plt.figure(figsize=(10, 10))
plt.scatter(train_embeddings_tsne[:, 0], train_embeddings_tsne[:, 1], c=train_team)
plt.title("Train Embeddings (TSNE)")
plt.show()

# Save the train embeddings to a file
np.save(os.path.join(args.model_dir, "train_embeddings.npy"), train_embeddings)

# Evaluate the model on the test dataset
tf.logging.info("Evaluating the model on the TEST portion!")

dataset = multi_modal_dataset.test(args.data_dir, args.embed_dir)
dataset = dataset.batch(1684)
dataset = dataset.prefetch(1)
dataset = dataset.make_initializable_iterator()
dataset_next = dataset.get_next()

# Obtain the test labels
test_images, test_tweets, test_user_ids, test_team = sess.run(dataset_next)

fd_test_renamed = {
    model.images: test_images,
    model.tweets: test_tweets,
    model.user_ids: test_user_ids,
    model.team: test_team
}

test_loss, test_acc = sess.run([model.total_loss, model.class_acc], fd_test_renamed)

tf.logging.info("Test loss: {:.4f}, Test accuracy: {:.4f}".format(test_loss, test_acc))

# Visualize the test embeddings using TSNE
test_embeddings = sess.run(model.tweets_dense, fd_test_renamed)
test_embeddings_tsne = tsne.fit_transform(test_embeddings)

plt.figure(figsize=(10, 10))
plt.scatter(test_embeddings_tsne[:, 0], test_embeddings_tsne[:, 1], c=test_team)
plt.title("Test Embeddings (TSNE)")
plt.show()

# Save the test embeddings to a file
np.save(os.path.join(args.model_dir, "test_embeddings.npy"), test_embeddings)
