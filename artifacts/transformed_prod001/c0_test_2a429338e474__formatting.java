package tonius.simplyjetpacks.util;

import net.minecraft.item.ItemStack;
import net.minecraft.nbt.NBTTagCompound;

public abstract class StackUtils {

  public static NBTTagCompound retrieveNBT(ItemStack stack) {
    if (!stack.hasTagCompound()) {
      stack.setTagCompound(new NBTTagCompound());
    }
    return stack.getTagCompound();
  }

  public static boolean fetchNBTBoolean(ItemStack stack, String tagName, boolean defaultValue) {
    NBTTagCompound nbt = retrieveNBT(stack);
    return nbt.hasKey(tagName) ? nbt.getBoolean(tagName) : defaultValue;
  }
}
