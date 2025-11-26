import * as React from "react";
import { Container, Typography, Box } from "@mui/material";

export default function Privacy() {
  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 6 }}>
      <Box>
        <Typography variant="h4" gutterBottom>
          Privacy Policy
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Last Updated: {new Date().toLocaleDateString()}
        </Typography>

        <Typography variant="body1" paragraph>
          This Privacy Policy explains how we collect, use, and protect your
          information when you use our software application (“the Service”),
          which may be deployed through cloud marketplaces such as Microsoft
          Azure, Google Cloud Platform, or other environments.
        </Typography>

        <Typography variant="h6" gutterBottom>
          1. Information We Collect
        </Typography>
        <Typography variant="body1" paragraph>
          Our Service processes data that you or your organization provide,
          which may include documents, files, or other information ingested
          during use. We do not collect personal information for advertising or
          marketing purposes. Any operational data is limited to logs and
          metadata necessary for service functionality, security, and
          troubleshooting.
        </Typography>

        <Typography variant="h6" gutterBottom>
          2. How We Use Information
        </Typography>
        <Typography variant="body1" paragraph>
          Data provided through the Service is used solely for:
        </Typography>
        <ul>
          <li>Performing the functionality you request (e.g., analytics, search, classification).</li>
          <li>Ensuring service reliability, monitoring, and security.</li>
          <li>Improving performance and user experience.</li>
        </ul>

        <Typography variant="h6" gutterBottom>
          3. Data Storage & Security
        </Typography>
        <Typography variant="body1" paragraph>
          If deployed in your organization’s cloud environment (e.g., Azure
          subscription or Google Cloud project), your data remains within your
          infrastructure. We do not access, transmit, or store your data outside
          of your controlled environment. We implement industry-standard
          security practices to safeguard any operational or diagnostic
          information we manage.
        </Typography>

        <Typography variant="h6" gutterBottom>
          4. Third Parties
        </Typography>
        <Typography variant="body1" paragraph>
          We do not sell or rent your data to third parties. Cloud marketplace
          providers (e.g., Microsoft, Google) may collect their own usage data
          per their privacy policies, which are independent of this Service.
        </Typography>

        <Typography variant="h6" gutterBottom>
          5. Compliance
        </Typography>
        <Typography variant="body1" paragraph>
          We comply with applicable data protection and privacy laws, including
          the General Data Protection Regulation (GDPR) where relevant. If your
          organization requires a Data Processing Agreement (DPA), please
          contact us.
        </Typography>

        <Typography variant="h6" gutterBottom>
          6. Your Rights
        </Typography>
        <Typography variant="body1" paragraph>
          Depending on your jurisdiction, you may have rights regarding access,
          correction, deletion, or restriction of your personal information. As
          the Service is typically deployed within your organization’s cloud
          environment, you should contact your system administrator to exercise
          these rights.
        </Typography>

        <Typography variant="h6" gutterBottom>
          7. Contact Us
        </Typography>
        <Typography variant="body1" paragraph>
          If you have questions about this Privacy Policy or our data practices,
          please contact us at{" "}
          <a href="mailto:products_ediscovery@plumgenai.com">eDiscovery Products</a>.
        </Typography>
      </Box>
    </Container>
  );
}
