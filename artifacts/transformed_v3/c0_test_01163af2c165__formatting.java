@SuppressWarnings("unchecked")
public class Password extends StdCommand {
  public Password() {}

  private String[] access = {"PASSWORD"};

  public String[] getAccessWords() {
    return access;
  }

  public boolean execute(MOB mob, Vector commands, int metaFlags) throws java.io.IOException {
    PlayerStats pstats = mob.playerStats();
    if (pstats == null) return false;
    if (mob.isMonster()) return false;
    String old = mob.session().prompt("Enter your old password : ");
    String nep = mob.session().prompt("Enter a new password    : ");
    String ne2 = mob.session().prompt("Enter new password again: ");
    if (!pstats.password().equals(old)) {
      mob.tell("Your old password was not entered correctly.");
      return false;
    }
    if (!nep.equals(ne2)) {
      mob.tell("Your new password was not entered the same way twice!");
      return false;
    }
    pstats.setPassword(nep);
    mob.tell("Your password has been changed.");
    if (pstats.getAccount() != null) CMLib.database().DBUpdateAccount(pstats.getAccount());
    CMLib.database().DBUpdatePassword(mob.Name(), nep);
    return false;
  }

  public boolean canBeOrdered() {
    return false;
  }
}
