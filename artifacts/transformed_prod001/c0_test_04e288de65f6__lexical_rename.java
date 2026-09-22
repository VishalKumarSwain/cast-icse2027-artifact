public class HelpFactory{

    public IHelpProvider getHelp() throws IllegalAccessException {
        try{
            Class<?> clazz_renamed = Class.forName("HelpProvider");

            for (Method method : clazz_renamed.getMethods()){
                if(method.getName().equals("getHelp")){
                    return (IHelpProvider) clazz_renamed.getDeclaredConstructor().newInstance();
                }
            }

            throw new IllegalAccessException("Could not instantiate HelpProvider. Method getHelp does not exist in this class.");
        } 
        catch(Exception e){
            throw new IllegalAccessException("Error while instantiating "+e.getMessage());
        }
     
    }
} 

