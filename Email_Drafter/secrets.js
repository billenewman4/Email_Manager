import { SecretManagerServiceClient } from '@google-cloud/secret-manager';

const client = new SecretManagerServiceClient();

async function getSecret(secretName) {
  try {
    const [version] = await client.accessSecretVersion({
      name: `projects/${process.env.GCP_PROJECT_ID}/secrets/${secretName}/versions/latest`,
    });

    return version.payload.data.toString();
  } catch (error) {
    console.error(`Failed to access secret ${secretName} from Secret Manager:`, error.message);
    return process.env[secretName];
  }
}

export { getSecret };