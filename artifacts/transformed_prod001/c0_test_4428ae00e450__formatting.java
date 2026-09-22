public class MleImageActor extends MleActor implements IImageActor {
  // The properties exposed in the DWP are "filename".

  /** Contains the name of the image file to display. */
  public MleImageProperty filename = null;

  /** The default constructor. */
  public MleImageActor() {
    super();
  }

  /**
   * Initialize the actor.
   *
   * <p>This method is a hook to do any initialization after property values are inserted into the
   * actor when the actor is directly loaded by MleDppLoader.mleLoadGroup() or indirectly by
   * MleDppLoader.mleLoadScene(). Typically, the actor may schedule itself or initialize its role
   * here. The base init() function does nothing. Use init() to initialize the actor after the
   * actor's member variables (i.e., properties) have been loaded by MleDppLoader.mleLoadGroup() or
   * MleDppLoader.mleLoadScene(). init() is called after the actor's data has been loaded into
   * memory, so this is the safest time to perform initialization and synchronization with the rest
   * of the environment.
   *
   * <p>The MleImageActor will push the filename to its associated role.
   *
   * @throws MleRuntimeException This exception is thrown if the actor can not be successfully
   *     initialized.
   * @see com.wizzer.mle.runtime.core.MleActor#init()
   */
  public void init() throws MleRuntimeException {
    // Update the Role by pushing the property values.
    filename.push(this);
  }

  /**
   * Dispose all resources associated with the Actor.
   *
   * @throws MleRuntimeException This exception is thrown if the actor can not be successfully
   *     initialized.
   * @see com.wizzer.mle.runtime.core.MleActor#dispose()
   */
  public void dispose() throws MleRuntimeException {
    // Do nothing for now.
  }

  /**
   * Get the value of the property with the specified name.
   *
   * <p>The <code>MleImageActor</code> has one property called <i>filename</i>
   *
   * @param name The name of the property as a <code>String</code>. Valid properties are
   *     <ul>
   *       <li>filename
   *     </ul>
   *
   * @return The property value is returned as an <code>Object</code>.
   * @throws MleRuntimeException This exception is thrown if the specified property can not be
   *     retrieved.
   * @see com.wizzer.mle.runtime.core.IMleObject#getProperty(java.lang.String)
   */
  public Object getProperty(String name) throws MleRuntimeException {
    if (name != null) {
      if (name.equals("filename")) return filename;
    }

    // Specified name does not exist.
    throw new MleRuntimeException("MleImageActor: Unable to get property " + name + ".");
  }

  /**
   * Set the value of the property with the specified name.
   *
   * @param name The name of the property as a <code>String</code>. Valid properties are
   *     <ul>
   *       <li>filename
   *     </ul>
   *
   * @param property The property to set.
   * @throws MleRuntimeException This exception is thrown if the specified property can not be set.
   * @see com.wizzer.mle.runtime.core.IMleObject#setProperty(java.lang.String, IMleProp)
   */
  public void setProperty(String name, IMleProp property) throws MleRuntimeException {
    if (name != null) {
      try {
        if (name.equals("filename")) {
          // Read the data in from the input stream.
          DataInputStream in = new DataInputStream(property.getStream());
          byte[] data = new byte[property.getLength()];
          in.readFully(data);

          // Create an image property and initialize it.
          if (property.getType() == IMleProp.PROP_TYPE_MEDIAREF) {
            // Assume it's coming from the DPP and data is an index into
            // the DPP Table-of-Contents.
            Integer index = new Integer(new String(data));

            // Retrieve the name from the DPP.
            try {
              filename = new MleImageProperty();
              MleMediaRef mref = MleDppLoader.getInstance().mleLoadMediaRef(index.intValue());
              filename.setProperty(mref);
            } catch (MleDppException ex) {
              throw new MleRuntimeException(ex.getMessage());
            }

            // Notify property change listeners.
            notifyPropertyChange("filename", null, null);
          } else {
            filename = new MleImageProperty();
            MleImageMediaRef mref = new MleImageMediaRef();
            mref.registerMedia(0, data.length, data);
            filename.setProperty(mref);

            // Notify property change listeners.
            notifyPropertyChange("filename", null, null);
          }

          return;
        }
      } catch (IOException ex) {
        throw new MleRuntimeException("MleImageActor: Unable to set property " + name + ".");
      }
    }

    // Specified name does not exist.
    throw new MleRuntimeException("MleImageActor: Unable to set property " + name + ".");
  }

  /**
   * Set the value of the property with the specified name.
   *
   * @param name The name of the property as a <code>String</code>.
   * @param length The length of each property, in bytes.
   * @param nElements The number of elements in the array, each of size <b>length</b>.
   * @param value The value of the property to set.
   * @throws MleRuntimeException This exception is thrown if the specified property can not be set.
   * @see com.wizzer.mle.runtime.core.IMleObject#setPropertyArray(java.lang.String, int, int,
   *     java.io.ByteArrayInputStream)
   */
  public void setPropertyArray(String name, int length, int nElements, ByteArrayInputStream value)
      throws MleRuntimeException {
    throw new MleRuntimeException("MleImageActor: Unable to set property array " + name + ".");
  }

  /**
   * Get the width of the image.
   *
   * @return An integer value is returned.
   */
  public int getWidth() {
    return filename.getWidth(this);
  }

  /**
   * Get the height of the image.
   *
   * @return An integer value is returned.
   */
  public int getHeight() {
    return filename.getHeight(this);
  }
}
