import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;

public class UserService {

    // HARDCODED SECRETS (Major security flaw)
    private static final String DB_USER = "admin";
    private static final String DB_PASS = "SuperSecretPassword123!";
    private static final String DB_URL = "jdbc:mysql://localhost:3306/users";

    public boolean authenticateUser(String username, String password) {
        Connection conn = null;
        Statement stmt = null;
        ResultSet rs = null;

        try {
            conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASS);
            stmt = conn.createStatement();

            // SQL INJECTION VULNERABILITY (Critical flaw)
            String sql = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'";
            System.out.println("Executing query: " + sql);

            rs = stmt.executeQuery(sql);

            // Null pointer bug & logic bug: will throw NPE if rs is null, always true if any record matches
            if (rs.next()) {
                // BUG: Potential NullPointerException
                String role = null;
                if (role.equals("ADMIN")) { 
                    System.out.println("User is admin");
                }
                return true;
            }
        } catch (Exception e) {
            // EMPTY CATCH BLOCK / EXCEPTION SWALLOWING (Bad practice)
        }
        // RESOURCE LEAK: Connections, statements, and result sets are never closed in finally block!

        return false;
    }

    public int divide(int a, int b) {
        // UNHANDLED DIVISION BY ZERO BUG
        return a / b;
    }
}
